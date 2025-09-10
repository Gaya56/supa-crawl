// Deno imports - https://supabase.com/docs/guides/functions/import-maps
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7'

// Types
interface PredictionMarket {
  website_name: string
  bet_title: string
  odds: string
  summary: string
  market_category: string | null
  betting_options: string | null
  probability_percentage: number | null
  volume_info: string | null
}

interface MarketsByCategory {
  [key: string]: Array<{
    site: string
    title: string
    odds: string
    probability: number | null
    volume: string | null
  }>
}

serve(async (req: Request) => {
  try {
    console.log('Daily report function started')

    // Initialize Supabase admin client
    // Docs: https://supabase.com/docs/guides/functions/connect-to-postgres
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Missing Supabase credentials')
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    })

    // Query last 24 hours of prediction market data
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    
    console.log(`Querying data since: ${yesterday.toISOString()}`)
    
    const { data: markets, error } = await supabase
      .from('Testing')
      .select(`
        website_name,
        bet_title,
        odds,
        summary,
        market_category,
        betting_options,
        probability_percentage,
        volume_info
      `)
      .gte('timestamp', yesterday.toISOString())
      .order('volume_info', { ascending: false, nullsFirst: false })

    if (error) {
      console.error('Database query error:', error)
      throw error
    }

    console.log(`Found ${markets?.length || 0} markets`)

    if (!markets || markets.length === 0) {
      return new Response(
        JSON.stringify({ message: 'No markets found in last 24 hours' }),
        { headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Group markets by category
    const categorizedMarkets: MarketsByCategory = markets.reduce((acc, market) => {
      const category = market.market_category || 'Uncategorized'
      if (!acc[category]) acc[category] = []
      acc[category].push({
        site: market.website_name,
        title: market.bet_title,
        odds: market.odds,
        probability: market.probability_percentage,
        volume: market.volume_info
      })
      return acc
    }, {} as MarketsByCategory)

    // Get unique websites
    const websites = [...new Set(markets.map((m: PredictionMarket) => m.website_name))]
    
    // Prepare market summary
    const marketSummary = Object.entries(categorizedMarkets)
      .map(([category, items]) => `${category}: ${items.length} markets`)
      .join(', ')

    console.log('Market summary:', marketSummary)

    // Call OpenAI for analysis
    // Docs: https://platform.openai.com/docs/api-reference/chat/create
    const openaiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiKey) {
      throw new Error('Missing OpenAI API key')
    }

    console.log('Calling OpenAI for analysis...')
    
    const openAIResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a prediction market analyst. Analyze betting trends and provide insights in HTML format with these sections:
            1. Executive Summary (key findings in 3-4 bullets)
            2. Market Trends by Category (highlight high-volume and shifting markets)
            3. Notable Movements (significant probability changes or new markets)
            4. Investment Opportunities (markets with potential value)
            Format as clean HTML with <h2> headers and <ul>/<li> for lists.`
          },
          {
            role: 'user',
            content: `Analyze ${markets.length} prediction markets from the last 24 hours across ${websites.length} platforms:

Categories: ${marketSummary}

Full data:
${JSON.stringify(categorizedMarkets, null, 2)}`
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    if (!openAIResponse.ok) {
      const errorText = await openAIResponse.text()
      console.error('OpenAI error:', errorText)
      throw new Error(`OpenAI API failed: ${openAIResponse.status}`)
    }

    const aiData = await openAIResponse.json()
    const aiAnalysis = aiData.choices[0].message.content

    // Create HTML email
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    h1 {
      color: #1a1a1a;
      border-bottom: 3px solid #007bff;
      padding-bottom: 10px;
    }
    h2 {
      color: #444;
      margin-top: 25px;
    }
    .header-info {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 8px;
      margin: 20px 0;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      margin: 15px 0;
    }
    .stat-box {
      background: #007bff;
      color: white;
      padding: 10px;
      border-radius: 5px;
      text-align: center;
    }
    .stat-box .number {
      font-size: 24px;
      font-weight: bold;
    }
    .stat-box .label {
      font-size: 14px;
      opacity: 0.9;
    }
    ul {
      padding-left: 20px;
    }
    li {
      margin: 8px 0;
    }
  </style>
</head>
<body>
  <h1>📊 Daily Prediction Market Report</h1>
  
  <div class="header-info">
    <strong>Report Date:</strong> ${new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })}<br>
    <strong>Analysis Period:</strong> Last 24 hours<br>
    <strong>Data Sources:</strong> ${websites.join(', ')}
  </div>
  
  <div class="stats">
    <div class="stat-box">
      <div class="number">${markets.length}</div>
      <div class="label">Total Markets</div>
    </div>
    <div class="stat-box">
      <div class="number">${Object.keys(categorizedMarkets).length}</div>
      <div class="label">Categories</div>
    </div>
    <div class="stat-box">
      <div class="number">${websites.length}</div>
      <div class="label">Platforms</div>
    </div>
  </div>
  
  ${aiAnalysis}
  
  <hr style="margin-top: 40px; border: 1px solid #eee;">
  <p style="font-size: 12px; color: #666; text-align: center;">
    This report was automatically generated by Crawl4AI Daily Reporter. 
    Data sourced from ${websites.join(', ')}.
  </p>
</body>
</html>`

    console.log('HTML email created, sending via Resend...')

    // Send email via Resend
    // Docs: https://resend.com/docs/api-reference/emails/send-email
    const resendKey = Deno.env.get('RESEND_API_KEY')
    const emailTo = Deno.env.get('REPORT_EMAIL_TO')
    
    if (!resendKey || !emailTo) {
      throw new Error('Missing Resend configuration')
    }

    const emailResponse = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'Prediction Markets <reports@yourdomain.com>',
        to: emailTo.split(',').map(email => email.trim()),
        subject: `📈 Daily Prediction Market Analysis - ${new Date().toLocaleDateString()}`,
        html: htmlContent
      })
    })

    if (!emailResponse.ok) {
      const errorText = await emailResponse.text()
      console.error('Resend error:', errorText)
      throw new Error(`Email sending failed: ${emailResponse.status}`)
    }

    const emailResult = await emailResponse.json()
    console.log('Email sent successfully:', emailResult.id)

    // Return success response
    return new Response(
      JSON.stringify({ 
        success: true, 
        markets_analyzed: markets.length,
        categories: Object.keys(categorizedMarkets).length,
        email_id: emailResult.id,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' } 
      }
    )
    
  } catch (error) {
    console.error('Function error:', error)
    return new Response(
      JSON.stringify({ 
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
})