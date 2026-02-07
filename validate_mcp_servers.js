const axios = require('axios');

async function checkServerStatus(name, port, description) {
  try {
    const response = await axios.get(`http://localhost:${port}/`);
    const isHealthy = response.data.status === 'healthy';
    
    console.log(`${name} (Port ${port}): ${isHealthy ? 'ACTIVE' : 'ISSUE'} - ${description}`);
    console.log(`  - Initialized: ${response.data.initialized || 'N/A'}`);
    console.log(`  - Authenticated: ${response.data.authenticated || response.data.auth_required === false || 'N/A'}`);
    console.log(`  - Capabilities: ${response.data.capabilities?.length || 0}`);
    
    return { name, port, status: isHealthy ? 'ACTIVE' : 'ISSUE', details: response.data };
  } catch (error) {
    // Server might not be running or requires auth setup
    console.log(`${name} (Port ${port}): NOT RUNNING - ${description}`);
    console.log(`  - Error: ${error.message}`);
    return { name, port, status: 'NOT_RUNNING', details: null };
  }
}

async function validateAllServers() {
  console.log('Validating MCP Server Status...\n');
  
  const servers = [
    { name: 'Context7 MCP', port: 8080, desc: 'Context analysis and data retrieval' },
    { name: 'Gmail MCP', port: 8081, desc: 'Email operations (requires OAuth setup)' },
    { name: 'LinkedIn MCP', port: 8082, desc: 'LinkedIn posting and engagement (requires OAuth setup)' },
    { name: 'WhatsApp MCP', port: 8083, desc: 'WhatsApp messaging (requires API credentials)' }
  ];
  
  const results = [];
  
  for (const server of servers) {
    const result = await checkServerStatus(server.name, server.port, server.desc);
    results.push(result);
    console.log('');
  }
  
  // Summary
  console.log('=== SUMMARY ===');
  const active = results.filter(r => r.status === 'ACTIVE').length;
  const issues = results.filter(r => r.status === 'ISSUE').length;
  const notRunning = results.filter(r => r.status === 'NOT_RUNNING').length;
  
  console.log(`Active servers: ${active}/4`);
  console.log(`Servers with issues: ${issues}/4`);
  console.log(`Servers not running: ${notRunning}/4`);
  
  console.log('\n=== DETAILED STATUS ===');
  results.forEach(result => {
    console.log(`${result.name}: ${result.status}`);
  });
  
  // Status report
  console.log('\n=== REPORT ===');
  console.log('ACTIVE servers:');
  results.filter(r => r.status === 'ACTIVE').forEach(r => {
    console.log(`  - ${r.name} (port ${r.port})`);
  });
  
  console.log('\nBLOCKED servers (require setup):');
  results.filter(r => r.status !== 'ACTIVE').forEach(r => {
    if (r.name === 'Gmail MCP' || r.name === 'LinkedIn MCP' || r.name === 'WhatsApp MCP') {
      console.log(`  - ${r.name}: Requires OAuth credentials or API keys to be set as environment variables`);
    } else if (r.status === 'NOT_RUNNING') {
      console.log(`  - ${r.name}: Not running (may have crashed due to missing environment variables)`);
    } else {
      console.log(`  - ${r.name}: Has configuration issues`);
    }
  });
  
  const allOperational = results.every(r => r.status === 'ACTIVE');
  console.log(`\nAI Employee system operational: ${allOperational ? 'YES' : 'NO - Additional setup required'}`);
  
  return results;
}

validateAllServers().catch(console.error);