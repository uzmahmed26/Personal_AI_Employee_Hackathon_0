const { spawn } = require('child_process');
const path = require('path');

console.log('Starting all MCP servers for Personal AI Employee...');

// Define server configurations
const servers = [
  {
    name: 'Context7 MCP',
    path: path.join(__dirname, 'MCP_SERVERS', 'context7_mcp', 'server.js'),
    port: 8080
  },
  {
    name: 'Gmail MCP',
    path: path.join(__dirname, 'MCP_SERVERS', 'gmail_mcp', 'server.js'),
    port: 8081
  },
  {
    name: 'LinkedIn MCP',
    path: path.join(__dirname, 'MCP_SERVERS', 'linkedin_mcp', 'server.js'),
    port: 8082
  },
  {
    name: 'WhatsApp MCP',
    path: path.join(__dirname, 'MCP_SERVERS', 'whatsapp_mcp', 'server.js'),
    port: 8083
  }
];

// Store spawned processes
const processes = [];

// Function to start a server
function startServer(server) {
  console.log(`Starting ${server.name} on port ${server.port}...`);

  const childProcess = spawn('node', [server.path], {
    cwd: __dirname,
    env: Object.assign({}, process.env, { PORT: server.port.toString() })
  });

  childProcess.stdout.on('data', (data) => {
    console.log(`${server.name} (${server.port}): ${data.toString().trim()}`);
  });

  childProcess.stderr.on('data', (data) => {
    console.error(`${server.name} (${server.port}) ERROR: ${data.toString().trim()}`);
  });

  childProcess.on('close', (code) => {
    console.log(`${server.name} (${server.port}) process exited with code ${code}`);
  });

  processes.push({ name: server.name, process: childProcess });
}

// Start all servers
servers.forEach(server => {
  startServer(server);
});

console.log('\nAll MCP servers started!');
console.log('Press Ctrl+C to stop all servers...');

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down all MCP servers...');
  processes.forEach(({ name, process: proc }) => {
    console.log(`Terminating ${name}...`);
    proc.kill();
  });
  process.exit(0);
});