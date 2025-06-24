/**
 * Beispiel: Raggadon in JavaScript/Node.js-Projekten verwenden
 */

const RAGGADON_URL = 'http://127.0.0.1:8000';
const PROJECT_NAME = 'MeinJSProjekt'; // Ändere dies für jedes Projekt

/**
 * Speichert wichtige Informationen im Projektgedächtnis
 */
async function saveToMemory(content, role = 'user') {
    try {
        const response = await fetch(`${RAGGADON_URL}/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                project: PROJECT_NAME,
                role: role,
                content: content
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Gespeichert! Tokens: ${data.tokens_used}, Kosten: $${data.estimated_cost_usd.toFixed(4)}`);
            return data;
        } else {
            console.error('❌ Fehler:', await response.text());
            return null;
        }
    } catch (error) {
        console.error('❌ Netzwerkfehler:', error);
        return null;
    }
}

/**
 * Sucht relevante Informationen im Projektgedächtnis
 */
async function searchMemory(query) {
    try {
        const params = new URLSearchParams({
            project: PROJECT_NAME,
            query: query
        });

        const response = await fetch(`${RAGGADON_URL}/search?${params}`);

        if (response.ok) {
            const data = await response.json();
            console.log(`🔍 ${data.results.length} Ergebnisse gefunden`);
            
            data.results.forEach(result => {
                console.log(`\n📄 ${result.role}: ${result.content.substring(0, 100)}...`);
                console.log(`   Ähnlichkeit: ${result.similarity.toFixed(2)}`);
            });
            
            return data;
        } else {
            console.error('❌ Fehler:', await response.text());
            return null;
        }
    } catch (error) {
        console.error('❌ Netzwerkfehler:', error);
        return null;
    }
}

// Beispiel-Verwendung:
(async () => {
    // Wichtige Projekt-Info speichern
    await saveToMemory('Die React-App verwendet Redux für State Management');
    await saveToMemory('Alle API-Calls gehen über den ApiService in src/services/api.js');
    
    // Nach Informationen suchen
    await searchMemory('state management');
    await searchMemory('api service');
})();