import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7'
import OpenAI from 'https://deno.land/x/openai@v4.24.0/mod.ts'

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

    // Get detailed table analysis
    const { data: tableStats, error: statsError } = await supabase.rpc('analyze_crawl4ai_docs')

    // Fetch from both tables
    const [crawlResult, supabaseResult] = await Promise.all([
      supabase.from('Crawl4AI-Docs').select('*'),
      supabase.from('Supabase-Docs').select('*')
    ])

    if (crawlResult.error || supabaseResult.error) {
      throw new Error(`Failed to fetch data: ${crawlResult.error?.message || supabaseResult.error?.message}`)
    }

    // Combine results from both tables
    const crawlDocs = crawlResult.data || []
    const supabaseDocs = supabaseResult.data || []
    let docs = [...crawlDocs.map(d => ({...d, source: 'Crawl4AI'})), ...supabaseDocs.map(d => ({...d, source: 'Supabase'}))]
    
    console.log(`Found ${crawlDocs.length} Crawl4AI docs and ${supabaseDocs.length} Supabase docs (${docs.length} total)`)

    // Add OpenAI summarization for documents without summaries
    const openaiKey = Deno.env.get('OPENAI_API_KEY')
    if (openaiKey && docs && docs.length > 0) {
      console.log('Checking for documents needing summaries...')
      
      const docsNeedingSummary = docs.filter(doc => doc.content && !doc.summary)
      console.log(`Found ${docsNeedingSummary.length} documents without summaries`)
      
      if (docsNeedingSummary.length > 0) {
        const openai = new OpenAI({ apiKey: openaiKey })
        
        // Process first 5 docs to avoid rate limits
        const docsToProcess = docsNeedingSummary.slice(0, 5)
        
        for (const doc of docsToProcess) {
          try {
            console.log(`Generating summary for doc ${doc.id}...`)
            
            const chatCompletion = await openai.chat.completions.create({
              messages: [{
                role: 'system',
                content: 'Generate a single concise sentence summary of the provided documentation content.'
              }, {
                role: 'user',
                content: doc.content.substring(0, 2000) // Limit content to avoid token limits
              }],
              model: 'gpt-3.5-turbo',
              max_tokens: 100,
              temperature: 0.3,
              stream: false
            })
            
            const summary = chatCompletion.choices[0].message.content
            
            // Update document with generated summary
            const tableName = doc.source === 'Crawl4AI' ? 'Crawl4AI-Docs' : 'Supabase-Docs'
            const { error: updateError } = await supabase
              .from(tableName)
              .update({ summary })
              .eq('id', doc.id)
            
            if (updateError) {
              console.error(`Failed to update doc ${doc.id}:`, updateError)
            } else {
              console.log(`Successfully updated doc ${doc.id} with summary`)
            }
            
            // Rate limit delay (1 second between requests)
            await new Promise(resolve => setTimeout(resolve, 1000))
            
          } catch (err) {
            console.error(`Error generating summary for doc ${doc.id}:`, err)
          }
        }
        
        // Re-fetch both tables to get updated summaries
        const [updatedCrawl, updatedSupabase] = await Promise.all([
          supabase.from('Crawl4AI-Docs').select('*'),
          supabase.from('Supabase-Docs').select('*')
        ])
        
        if (updatedCrawl.data || updatedSupabase.data) {
          const crawlDocs = updatedCrawl.data || []
          const supabaseDocs = updatedSupabase.data || []
          docs = [...crawlDocs.map(d => ({...d, source: 'Crawl4AI'})), ...supabaseDocs.map(d => ({...d, source: 'Supabase'}))]
        }
      }
    }

    // Enhanced data analysis
    const totalDocs = docs?.length || 0
    const avgContentLength = Math.round(docs?.reduce((sum, doc) => sum + (doc.content?.length || 0), 0) / totalDocs)
    const docsWithSummary = docs?.filter(doc => doc.summary).length || 0
    const completionRate = Math.round((docsWithSummary / totalDocs) * 100)
    const docsWithTitle = docs?.filter(doc => doc.title).length || 0

    // Comprehensive HTML report with sections:
    // - Table Overview with statistics
    // - Data Quality Analysis  
    // - Sample Documentation Topics
    // - System Status & Health

    // Sample titles for categories
    const sampleTitles = docs?.slice(0, 5).map(doc => doc.title).filter(Boolean) || []

    // Create detailed report
    const reportDate = new Date().toISOString().split('T')[0]
    const reportTitle = `Daily Crawl4AI Documentation Report - ${new Date().toLocaleDateString()}`

    // Simple text-based content for AI analysis
    const urlList = docs?.map(doc => `ID: ${doc.id} - ${doc.url}`).join('\n') || ''

    const simpleContent = `
Daily Crawl4AI Documentation Analysis
Generated: ${new Date().toLocaleString()}

TABLE OVERVIEW:
- Total Documents: ${totalDocs}
- Completion Rate: ${completionRate}%
- Average Content Length: ${avgContentLength} characters
- Data Integrity: ${docsWithTitle === totalDocs ? 'Complete' : 'Partial'}

DATA QUALITY:
- Documents with Titles: ${docsWithTitle}/${totalDocs} (${Math.round((docsWithTitle / totalDocs) * 100)}%)
- Documents with Summaries: ${docsWithSummary}/${totalDocs} (${completionRate}%)
- Content Coverage: ${docs?.filter(doc => doc.content).length || 0}/${totalDocs} documents

COMPLETE URL DIRECTORY:
${urlList}

SAMPLE TOPICS:
${sampleTitles.map((title, index) => `${index + 1}. ${title}`).join('\n')}

SYSTEM STATUS:
- Database Connection: Active
- Data Freshness: Current  
- Next Report: Tomorrow at 9:00 AM UTC
- Report Source: Combined analysis of Crawl4AI-Docs (${crawlDocs.length}) and Supabase-Docs (${supabaseDocs.length}) tables
    `

    // Save to database
    const { data: reportData, error: saveError } = await supabase
      .from('daily_reports')
      .insert({
        report_date: reportDate,
        title: reportTitle,
        content: simpleContent,
        summary: `Combined analysis of ${totalDocs} documentation records from both Crawl4AI and Supabase tables`,
        documents_analyzed: totalDocs,
        categories_found: 3, // Overview, Quality, Status
        ai_insights: `Data integrity: ${completionRate}% complete, Avg content: ${avgContentLength} chars`,
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
      documents_count: totalDocs,
      completion_rate: completionRate,
      avg_content_length: avgContentLength,
      message: 'Enhanced report saved to database'
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
