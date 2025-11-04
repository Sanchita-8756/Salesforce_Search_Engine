// script.js - Salesforce MCP Interface

const BACKEND_URL = 'http://localhost:8000';

// Utility function to display results
function displayResult(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

// Utility function to show error
function displayError(error) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div class="error">Error: ${error}</div>`;
}

// SOQL Query
document.getElementById('runSoqlBtn').addEventListener('click', async () => {
    const soql = document.getElementById('soqlInput').value.trim();
    if (!soql) {
        displayError('Please enter a SOQL query');
        return;
    }
    
    try {
        const response = await fetch(`${BACKEND_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `soql:${soql}` })
        });
        
        const data = await response.json();
        displayResult(data);
    } catch (error) {
        displayError(error.message);
    }
});

// Get Record
document.getElementById('getRecordBtn').addEventListener('click', async () => {
    const objectName = document.getElementById('objectName').value.trim();
    const recordId = document.getElementById('recordId').value.trim();
    
    if (!objectName || !recordId) {
        displayError('Please enter both object name and record ID');
        return;
    }
    
    try {
        const response = await fetch(`${BACKEND_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `get:${objectName}/${recordId}` })
        });
        
        const data = await response.json();
        displayResult(data);
    } catch (error) {
        displayError(error.message);
    }
});

// Describe Object
document.getElementById('describeBtn').addEventListener('click', async () => {
    const objectName = document.getElementById('objectName').value.trim();
    
    if (!objectName) {
        displayError('Please enter an object name');
        return;
    }
    
    try {
        const response = await fetch(`${BACKEND_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `describe:${objectName}` })
        });
        
        const data = await response.json();
        displayResult(data);
    } catch (error) {
        displayError(error.message);
    }
});

// Create Record
document.getElementById('createBtn').addEventListener('click', async () => {
    const objectName = document.getElementById('objectName').value.trim();
    const recordDataText = document.getElementById('recordData').value.trim();
    
    if (!objectName || !recordDataText) {
        displayError('Please enter object name and record data');
        return;
    }
    
    try {
        const recordData = JSON.parse(recordDataText);
        const response = await fetch(`${BACKEND_URL}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                command: `create:${objectName}`,
                payload: recordData
            })
        });
        
        const data = await response.json();
        displayResult(data);
    } catch (error) {
        displayError(error.message);
    }
});

// Update Record
document.getElementById('updateBtn').addEventListener('click', async () => {
    const objectName = document.getElementById('objectName').value.trim();
    const recordId = document.getElementById('recordId').value.trim();
    const recordDataText = document.getElementById('recordData').value.trim();
    
    if (!objectName || !recordId || !recordDataText) {
        displayError('Please enter object name, record ID, and record data');
        return;
    }
    
    try {
        const recordData = JSON.parse(recordDataText);
        const response = await fetch(`${BACKEND_URL}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                command: `update:${objectName}/${recordId}`,
                payload: recordData
            })
        });
        
        const data = await response.json();
        displayResult(data);
    } catch (error) {
        displayError(error.message);
    }
});

// Load sample SOQL on page load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('soqlInput').value = 'SELECT Id, Name, Type FROM Account LIMIT 10';
    document.getElementById('objectName').value = 'Account';
});
