import { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
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
    try {
      const response = await fetch('http://localhost:5000/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), firstName: firstName.trim(), lastName: lastName.trim() }),
      });
      const data = await response.json();
      if (data.error) { setError(data.error); } else { setResults(data); }
    } catch (err) {
      setError('Failed to connect to backend');
    } finally {
      setLoading(false);
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
          <button type="submit" disabled={loading}>{loading ? 'Deep Investigating...' : 'Deep Investigate'}</button>
        </form>
        {error && <div className="error">{error}</div>}
        {results && (
          <div className="results">
            <div className="results-header"><h2>🎯 Investigation Report</h2>{results.email_results && <p className="target-email">{results.email_results.email}</p>}{results.name_results && <p className="target-name">{results.name_results.full_name}</p>}</div>
            
            {results.name_results?.username_investigations && (
              <div className="section">
                <h3>🔤 Username Analysis (Auto-Investigated)</h3>
                <div className="username-analysis-grid">
                  {results.name_results.username_investigations.map((investigation, i) => (
                    <div key={i} className="username-analysis-card">
                      <div className="username-header">
                        <span className="username-text">{investigation.username}</span>
                        <div className={`probability-mini ${investigation.confidence.toLowerCase()}`}>
                          {investigation.probability}%
                        </div>
                      </div>
                      <div className="confidence-bar">
                        <div className={`confidence-fill ${investigation.confidence.toLowerCase()}`} style={{width: `${investigation.probability}%`}}></div>
                      </div>
                      <p className="confidence-text">{investigation.confidence} Confidence</p>
                      <p className="platforms-found">Found: {investigation.platforms_found}/{investigation.platforms_checked} platforms</p>
                      <div className="platform-mini-grid">
                        {investigation.details.filter(d => d.status === 'found').map((detail, j) => (
                          <a key={j} href={detail.url} target="_blank" rel="noopener noreferrer" className="platform-mini">
                            {detail.platform} ✅
                          </a>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.email_results?.google_dorks && (
              <div className="section google-dorks">
                <h3>🔍 Google Dorks (Email)</h3>
                <p className="detail">{results.email_results.google_dorks.note}</p>
                {results.email_results.google_dorks.regions && (<div className="stats">🇬🇧 UK/EU: {results.email_results.google_dorks.regions.uk_eu_count} | 🇺🇸 US: {results.email_results.google_dorks.regions.us_count}</div>)}
                <div className="dork-list">{results.email_results.google_dorks.dorks.map((dork, i) => (<div key={i} className={`dork-item priority-${dork.priority}`}><div className="dork-header"><span className={`region-badge ${dork.region.toLowerCase()}`}>{dork.region}</span><span className={`priority-badge ${dork.priority}`}>{dork.priority}</span>{dork.result_count && <span className="result-count">📊 {dork.result_count} results</span>}</div><code>{dork.query}</code><p className="dork-desc">{dork.description}</p><a href={`https://www.google.com/search?q=${encodeURIComponent(dork.query)}`} target="_blank" rel="noopener noreferrer" className="search-btn">Search</a></div>))}</div>
              </div>
            )}

            {results.name_results?.google_dorks && (
              <div className="section google-dorks">
                <h3>🔍 Google Dorks (Name)</h3>
                <p className="detail">{results.name_results.google_dorks.note}</p>
                {results.name_results.google_dorks.regions && (<div className="stats">🇬🇧 UK/EU: {results.name_results.google_dorks.regions.uk_eu_count} | 🇺🇸 US: {results.name_results.google_dorks.regions.us_count}</div>)}
                <div className="dork-list">{results.name_results.google_dorks.dorks.map((dork, i) => (<div key={i} className={`dork-item priority-${dork.priority}`}><div className="dork-header"><span className={`region-badge ${dork.region.toLowerCase()}`}>{dork.region}</span><span className={`priority-badge ${dork.priority}`}>{dork.priority}</span>{dork.result_count && <span className="result-count">📊 {dork.result_count} results</span>}</div><code>{dork.query}</code><p className="dork-desc">{dork.description}</p><a href={`https://www.google.com/search?q=${encodeURIComponent(dork.query)}`} target="_blank" rel="noopener noreferrer" className="search-btn">Search</a></div>))}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
export default App;
