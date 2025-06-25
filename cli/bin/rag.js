#!/usr/bin/env node

const { Command } = require('commander');
const axios = require('axios');
const chalk = require('chalk');
const ora = require('ora');
const path = require('path');
const fs = require('fs');
const os = require('os');

const program = new Command();
const RAGGADON_URL = process.env.RAGGADON_URL || 'http://127.0.0.1:8001';
const PROJECT_NAME = path.basename(process.cwd());

// Helper functions
function getConfigPath() {
  return path.join(os.homedir(), '.rag_config');
}

function getCurrentMode() {
  const configPath = getConfigPath();
  if (fs.existsSync(configPath)) {
    let mode = fs.readFileSync(configPath, 'utf8').trim();
    // Convert old verbose to active
    if (mode === 'verbose') {
      mode = 'active';
      fs.writeFileSync(configPath, mode);
    }
    return mode;
  }
  return 'active';
}

function formatTimestamp(timestampStr) {
  if (!timestampStr) return 'nie';
  
  try {
    const months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                   'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
    
    let dt;
    if (timestampStr.includes('T')) {
      // Remove timezone info if present
      const ts = timestampStr.split('+')[0].split('Z')[0];
      dt = new Date(ts + 'Z'); // Force UTC interpretation then convert to local
    } else {
      dt = new Date(timestampStr);
    }
    
    const day = dt.getDate();
    const month = months[dt.getMonth()];
    const year = dt.getFullYear();
    const hour = dt.getHours().toString().padStart(2, '0');
    const minute = dt.getMinutes().toString().padStart(2, '0');
    const second = dt.getSeconds().toString().padStart(2, '0');
    
    return `${day}.${month}.${year} - ${hour}:${minute}:${second} Uhr`;
  } catch (e) {
    return timestampStr;
  }
}

async function checkServerHealth() {
  try {
    await axios.get(`${RAGGADON_URL}/health`, { timeout: 3000 });
    return true;
  } catch (error) {
    return false;
  }
}

// Commands
program
  .name('rag')
  .description('🤖 Raggadon CLI - RAG für Claude Code')
  .version('1.0.0');

program
  .command('save')
  .description('Speichert wichtige Informationen für das aktuelle Projekt')
  .argument('<content>', 'Der zu speichernde Inhalt')
  .action(async (content) => {
    const spinner = ora('Speichere Information...').start();
    
    try {
      const response = await axios.post(`${RAGGADON_URL}/save`, {
        project: PROJECT_NAME,
        role: 'user',
        content: content
      }, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      });
      
      spinner.stop();
      
      if (response.data.success) {
        console.log(chalk.green(`✅ Gespeichert für Projekt '${PROJECT_NAME}': ${response.data.tokens_used || 0} Tokens`));
      } else {
        console.log(chalk.red(`❌ API Fehler: ${response.data.detail || 'Unbekannter Fehler'}`));
      }
    } catch (error) {
      spinner.stop();
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        console.log(chalk.red('❌ Raggadon läuft nicht! Starte mit: rag start'));
      } else {
        console.log(chalk.red(`❌ Fehler: ${error.message}`));
      }
    }
  });

program
  .command('search')
  .description('Sucht nach Informationen im aktuellen Projekt')
  .argument('<query>', 'Der Suchbegriff')
  .action(async (query) => {
    console.log(chalk.blue(`🔍 Suche nach '${query}' in Projekt '${PROJECT_NAME}'...`));
    
    try {
      const response = await axios.get(`${RAGGADON_URL}/search`, {
        params: { project: PROJECT_NAME, query: query },
        timeout: 10000
      });
      
      const results = response.data.results || [];
      console.log(chalk.cyan(`\n📚 ${results.length} Ergebnisse gefunden:\n`));
      
      results.slice(0, 5).forEach((result, index) => {
        const similarity = (result.similarity || 0).toFixed(2);
        const content = result.content.substring(0, 150) + '...';
        console.log(chalk.white(`${index + 1}. [${similarity}] ${content}`));
        console.log();
      });
    } catch (error) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        console.log(chalk.red('❌ Raggadon läuft nicht! Starte mit: rag start'));
      } else {
        console.log(chalk.red(`❌ Fehler: ${error.message}`));
      }
    }
  });

program
  .command('status')
  .description('Zeigt den Status des Raggadon Servers und Projekt-Statistiken')
  .action(async () => {
    const spinner = ora('Prüfe Server-Status...').start();
    
    const isRunning = await checkServerHealth();
    spinner.stop();
    
    if (isRunning) {
      console.log(chalk.green(`✅ Raggadon läuft auf ${RAGGADON_URL}`));
      console.log(chalk.blue(`📁 Aktuelles Projekt: ${PROJECT_NAME}`));
      console.log(chalk.yellow(`🔧 Modus: ${getCurrentMode()}`));
      console.log();
      
      // Get project statistics
      try {
        const response = await axios.get(`${RAGGADON_URL}/project/${PROJECT_NAME}/stats`, {
          timeout: 5000
        });
        
        const stats = response.data;
        console.log(chalk.cyan('📊 Projekt-Statistiken:'));
        console.log(`   💾 Gespeicherte Einträge: ${stats.total_memories || 0}`);
        console.log(`   🔤 Tokens diesen Monat: ${(stats.monthly_tokens || 0).toLocaleString()}`);
        console.log(`   💰 Geschätzte Kosten: $${(stats.estimated_monthly_cost_usd || 0).toFixed(4)}`);
        console.log(`   🤖 Embedding Model: ${stats.model || 'unknown'}`);
        console.log(`   💵 Preis: $${(stats.cost_per_1k_tokens || 0).toFixed(2)} pro 1K Tokens`);
        
        if (stats.first_activity) {
          console.log(`   🕐 Erste Aktivität: ${formatTimestamp(stats.first_activity)}`);
        }
        if (stats.last_activity) {
          console.log(`   🕐 Letzte Aktivität: ${formatTimestamp(stats.last_activity)}`);
        }
        
        const activities = stats.recent_activities || [];
        if (activities.length > 0) {
          console.log('\n📋 Letzte Aktivitäten:');
          activities.slice(0, 3).forEach(act => {
            console.log(`   • ${act.type}: ${act.tokens} Tokens`);
          });
        }
      } catch (error) {
        console.log('   ℹ️ Noch keine Statistiken für dieses Projekt vorhanden');
      }
    } else {
      console.log(chalk.red('❌ Raggadon läuft nicht!'));
      console.log(chalk.yellow('🚀 Starte mit: rag start'));
    }
  });

program
  .command('start')
  .description('Startet den Raggadon Server')
  .action(() => {
    console.log(chalk.blue('🚀 Starte Raggadon Server...'));
    
    const { spawn } = require('child_process');
    const serverPath = path.join(os.homedir(), 'Desktop/ars vivai/Raggadon/start_server.sh');
    
    if (fs.existsSync(serverPath)) {
      const child = spawn('bash', [serverPath], {
        detached: true,
        stdio: 'ignore'
      });
      child.unref();
      console.log(chalk.green('✅ Server gestartet im Hintergrund'));
    } else {
      console.log(chalk.red('❌ Server-Script nicht gefunden'));
      console.log(chalk.yellow('Erwarteter Pfad: ' + serverPath));
    }
  });

program
  .command('mode')
  .description('Ändert den Auto-Save Modus')
  .argument('[mode]', 'Modus: active, silent, ask, show')
  .action((mode) => {
    const configPath = getConfigPath();
    
    if (!mode || mode === 'show') {
      const currentMode = getCurrentMode();
      console.log(chalk.yellow(`🔧 Aktueller Modus: ${currentMode}`));
      return;
    }
    
    switch (mode.toLowerCase()) {
      case 'active':
      case 'a':
      case 'verbose':
      case 'v':
        fs.writeFileSync(configPath, 'active');
        console.log(chalk.green('✅ Active Mode aktiviert - Claude zeigt alle RAG-Speicherungen an'));
        break;
        
      case 'silent':
      case 's':
        fs.writeFileSync(configPath, 'silent');
        console.log(chalk.green('✅ Silent Mode aktiviert - RAG arbeitet im Hintergrund'));
        console.log(chalk.blue('   💡 Status sehen mit: rag status'));
        break;
        
      case 'ask':
      case 'question':
      case 'q':
        fs.writeFileSync(configPath, 'ask');
        console.log(chalk.green('✅ Ask Mode aktiviert - Frage vor jeder RAG-Operation'));
        break;
        
      default:
        console.log(chalk.red(`❌ Unbekannter Modus: ${mode}`));
        console.log('\nVerfügbare Modi:');
        console.log('  rag mode active   # Claude zeigt alle RAG-Speicherungen an');
        console.log('  rag mode silent   # Arbeite im Hintergrund (Status mit "rag status")');
        console.log('  rag mode ask      # Frage vor jeder Operation');
        console.log('  rag mode show     # Zeige aktuellen Modus');
    }
  });

program
  .command('init')
  .description('Initialisiert Raggadon für das aktuelle Projekt')
  .action(() => {
    const claudeMdTemplate = path.join(os.homedir(), 'Desktop/ars vivai/Raggadon/CLAUDE.md');
    const targetClaudeMd = path.join(process.cwd(), 'CLAUDE.md');
    
    if (fs.existsSync(targetClaudeMd)) {
      console.log(chalk.yellow('⚠️  CLAUDE.md already exists in this project'));
      // In a real implementation, we'd use inquirer for interactive prompts
      console.log(chalk.blue('Use --force to overwrite existing CLAUDE.md'));
      return;
    }
    
    if (fs.existsSync(claudeMdTemplate)) {
      fs.copyFileSync(claudeMdTemplate, targetClaudeMd);
      console.log(chalk.green(`✅ Raggadon integration added to ${process.cwd()}`));
      console.log(chalk.blue('📝 CLAUDE.md copied - Claude will now use Raggadon commands'));
    } else {
      console.log(chalk.red(`❌ Template not found at ${claudeMdTemplate}`));
    }
  });

// Default help
program.configureHelp({
  sortSubcommands: true,
});

// If no command provided, show help
if (process.argv.length <= 2) {
  console.log(chalk.cyan('🤖 Raggadon CLI - RAG für Claude Code\n'));
  console.log('Verwendung:');
  console.log('  rag save "Wichtige Info"    # Speichert Info für aktuelles Projekt');
  console.log('  rag search "keyword"        # Sucht im aktuellen Projekt');  
  console.log('  rag status                  # Prüft Server-Status');
  console.log('  rag start                   # Startet Raggadon Server');
  console.log('  rag mode <active|silent|ask|show>   # Ändert Auto-Save Modus');
  console.log('  rag init                    # Initialisiert Raggadon für Projekt');
  console.log();
  console.log(chalk.blue(`Aktuelles Projekt: ${PROJECT_NAME}`));
  process.exit(0);
}

program.parse();