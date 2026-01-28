import { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleInvestigate = async (e) => {
    e.preventDefault();
    if (!email.trim() && !(firstName.trim() && lastName.trim())) {
      setError('Please provide either an email address OR both first and last name');
      return;
    }
    setLoading(true);
    setError('');
    setResults(null);
    setProgress(0);
    
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 15;
      });
    }, 500);
    
    try {
      const response = await fetch('http://localhost:5000/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), firstName: firstName.trim(), lastName: lastName.trim() }),
      });
      const data = await response.json();
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        if (data.error) { setError(data.error); } else { setResults(data); }
        setLoading(false);
        setProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setError('Failed to connect to backend');
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>🔍 Advanced OSINT Tool</h1>
        <p className="subtitle">Deep investigation: Search by email, name, or both</p>
        <form onSubmit={handleInvestigate}>
          <div className="search-section"><h3>🔎 Search by Email</h3><input type="email" placeholder="Enter email address..." value={email} onChange={(e) => setEmail(e.target.value)} disabled={loading} /></div>
          <div className="divider"><span>OR</span></div>
          <div className="search-section"><h3>👤 Search by Name</h3><div className="name-inputs"><input type="text" placeholder="First Name" value={firstName} onChange={(e) => setFirstName(e.target.value)} disabled={loading} /><input type="text" placeholder="Last Name" value={lastName} onChange={(e) => setLastName(e.target.value)} disabled={loading} /></div></div>
          <button type="submit" disabled={loading}>{loading ? 'Investigating...' : 'Deep Investigate'}</button>
        </form>
        
        {loading && (
          <div className="progress-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${progress}%`}}></div>
            </div>
            <p className="progress-text">Deep scanning databases... {Math.round(progress)}%</p>
          </div>
        )}
        
        {error && <div className="error">{error}</div>}
        {results && (
          <div className="results">
            <div className="results-header"><h2>🎯 Investigation Report</h2>{results.email_results && <p className="target-email">{results.email_results.email}</p>}{results.name_results && <p className="target-name">{results.name_results.full_name}</p>}</div>
            
            {results.name_results?.username_investigations && (
              <div className="section">
                <h3>🔤 Username Analysis</h3>
                <div className="username-analysis-grid">
                  {results.name_results.username_investigations.map((investigation, i) => (
                    <div key={i} className="username-analysis-card">
                      <div className="username-header">
                        <span className="username-text">{investigation.username}</span>
                        <div className={`probability-mini ${investigation.confidence.toLowerCase()}`}>{investigation.probability}%</div>
                      </div>
                      <div className="confidence-bar"><div className={`confidence-fill ${investigation.confidence.toLowerCase()}`} style={{width: `${investigation.probability}%`}}></div></div>
                      <p className="confidence-text">{investigation.confidence} Confidence</p>
                      <p className="platforms-found">Found: {investigation.platforms_found}/{investigation.platforms_checked}</p>
                      <div className="platform-mini-grid">{investigation.details.filter(d => d.status === 'found').map((detail, j) => (<a key={j} href={detail.url} target="_blank" rel="noopener noreferrer" className="platform-mini">{detail.platform} ✅</a>))}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.email_results?.dark_web_mentions && (
              <div className="section dark-web">
                <h3>🕵️ Dark Web & Leak Databases</h3>
                <p className="detail">{results.email_results.dark_web_mentions.note}</p>
                <div className="platform-grid">
                  {results.email_results.dark_web_mentions.search_engines.map((engine, i) => (
                    <div key={i} className="platform-card"><a href={engine.url} target="_blank" rel="noopener noreferrer">{engine.name}</a><p className="platform-desc">{engine.description}</p></div>
                  ))}
                </div>
                <h4 style={{marginTop: '20px', color: '#667eea'}}>Leak Databases</h4>
                <div className="platform-grid">
                  {results.email_results.dark_web_mentions.leak_databases.map((db, i) => (
                    <div key={i} className="platform-card"><a href={db.url} target="_blank" rel="noopener noreferrer">{db.name}</a><p className="platform-desc">{db.note}</p></div>
                  ))}
                </div>
              </div>
            )}

            {results.email_results?.breaches && (
              <div className="section">
                <h3>🔒 Data Breaches (Multiple Sources)</h3>
                <div className="breach-sources">
                  {results.email_results.breaches.details.map((source, i) => (
                    <div key={i} className="source-item"><strong>{source.source}:</strong> {source.status}{source.count > 0 && <span> ({source.count} breaches)</span>}</div>
                  ))}
                </div>
                {results.email_results.breaches.found && results.email_results.breaches.breaches_found.length > 0 ? (
                  <div className="breach-list">{results.email_results.breaches.breaches_found.map((breach, i) => (<div key={i} className="breach-item"><h4>{breach.name}</h4><p className="breach-date">{breach.date}</p><p className="breach-data">{breach.data?.join(', ')}</p></div>))}</div>
                ) : (<p className="success">✅ No breaches found</p>)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
export default App;
