import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7'

serve(async (req: Request) => {
  try {
    console.log('Daily report function started')

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Missing Supabase credentials')
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Get data count from Crawl4AI-Docs
    const { count, error: countError } = await supabase
      .from('Crawl4AI-Docs')
      .select('*', { count: 'exact', head: true })

    if (countError) {
      throw new Error(`Failed to count data: ${countError.message}`)
    }

    console.log(`Found ${count} documents`)

    // Create simple report
    const reportDate = new Date().toISOString().split('T')[0]
    const reportTitle = `Daily Crawl4AI Documentation Report - ${new Date().toLocaleDateString()}`
    const simpleContent = `
    <h1>📚 Daily Report</h1>
    <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
    <p><strong>Documents Analyzed:</strong> ${count}</p>
    <p><strong>Status:</strong> System operational</p>
    `

    // Save to database
    const { data: reportData, error: saveError } = await supabase
      .from('daily_reports')
      .insert({
        report_date: reportDate,
        title: reportTitle,
        content: simpleContent,
        summary: `Analyzed ${count} documents`,
        documents_analyzed: count || 0,
        categories_found: 1,
        ai_insights: 'Simple daily check completed',
        status: 'completed'
      })
      .select()

    if (saveError) {
      throw new Error(`Failed to save: ${saveError.message}`)
    }

    console.log('Report saved:', reportData?.[0]?.id)

    return new Response(JSON.stringify({
      success: true,
      report_id: reportData?.[0]?.id,
      documents_count: count,
      message: 'Report saved to database'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error:', error)
    return new Response(JSON.stringify({
      error: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
})
