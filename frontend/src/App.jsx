import { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInvestigate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch('http://localhost:5000/api/investigate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data);
      }
    } catch (err) {
      setError('Failed to connect to backend. Make sure Flask is running!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>🔍 Advanced Email OSINT Tool</h1>
        <p className="subtitle">Deep investigation: breaches, reputation, social media, dark web & paste sites</p>

        <form onSubmit={handleInvestigate}>
          <input
            type="email"
            placeholder="Enter email address..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Deep Investigating...' : 'Deep Investigate'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {results && (
          <div className="results">
            <div className="results-header">
              <h2>🎯 Investigation Report</h2>
              <p className="target-email">{results.email}</p>
              <p className="timestamp">Generated: {new Date(results.timestamp).toLocaleString()}</p>
            </div>

            {/* Reputation Score */}
            {results.reputation && !results.reputation.error && (
              <div className="section reputation">
                <h3>📊 Email Reputation</h3>
                <div className={`reputation-badge ${results.reputation.reputation}`}>
                  {results.reputation.reputation?.toUpperCase() || 'UNKNOWN'}
                </div>
                {results.reputation.suspicious && (
                  <p className="warning">⚠️ Flagged as suspicious</p>
                )}
                <p>References found: {results.reputation.references || 0}</p>
              </div>
            )}

            {/* Paste Sites & Leaks */}
            {results.paste_sites && (
              <div className="section dark-web">
                <h3>📋 Paste Site Mentions</h3>
                {results.paste_sites.total_found > 0 ? (
                  <>
                    <p className="warning">⚠️ Found in {results.paste_sites.total_found} paste dumps!</p>
                    <div className="paste-list">
                      {results.paste_sites.found_pastes.map((paste, i) => (
                        <div key={i} className="paste-item">
                          <a href={paste.url} target="_blank" rel="noopener noreferrer">
                            {paste.title}
                          </a>
                          <p className="paste-time">{new Date(paste.time * 1000).toLocaleString()}</p>
                        </div>
                      ))}
                    </div>
                    <p className="detail">Check these pastes for potential data leaks</p>
                  </>
                ) : (
                  <p className="success">✅ No paste site mentions found</p>
                )}
              </div>
            )}

            {/* Dark Web Mentions */}
            {results.dark_web_mentions && (
              <div className="section dark-web">
                <h3>🕵️ Dark Web & Leak Databases</h3>
                <p className="detail">{results.dark_web_mentions.note}</p>
                
                <div className="darkweb-section">
                  <h4>Dark Web Search Engines:</h4>
                  <div className="link-grid">
                    {results.dark_web_mentions.search_engines.map((engine, i) => (
                      <div key={i} className="darkweb-card">
                        <a href={engine.url} target="_blank" rel="noopener noreferrer">
                          {engine.name}
                        </a>
                        <p className="engine-desc">{engine.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="darkweb-section">
                  <h4>Leak Databases:</h4>
                  <div className="link-grid">
                    {results.dark_web_mentions.leak_databases.map((db, i) => (
                      <div key={i} className="darkweb-card">
                        <a href={db.url} target="_blank" rel="noopener noreferrer">
                          {db.name}
                        </a>
                        <p className="engine-desc">{db.note}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Potential Names */}
            {results.potential_names && results.potential_names.length > 0 && (
              <div className="section">
                <h3>👤 Potential Identity</h3>
                {results.potential_names.map((name, i) => (
                  <div key={i} className="name-card">
                    {name.first && name.last ? (
                      <p className="potential-name">
                        <strong>{name.first} {name.last}</strong> 
                        <span className="name-type">({name.type})</span>
                      </p>
                    ) : (
                      <p>{name.note}</p>
                    )}
                    {name.numbers && (
                      <p className="detail">Possible birth year/date: {name.numbers.join(', ')}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Data Breaches */}
            <div className="section">
              <h3>🔒 Data Breaches</h3>
              {results.breaches.found ? (
                <div className="breach-info">
                  <p className="warning">⚠️ Found in {results.breaches.count} breaches!</p>
                  <div className="breach-list">
                    {results.breaches.breaches?.map((breach, i) => (
                      <div key={i} className="breach-item">
                        <h4>{breach.name}</h4>
                        <p className="breach-date">Date: {breach.date}</p>
                        <p className="breach-data">
                          Compromised: {breach.data?.join(', ') || 'Unknown'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="success">✅ No breaches found</p>
              )}
            </div>

            {/* Social Media */}
            <div className="section">
              <h3>📱 Social Media Presence</h3>
              <p className="stats">
                Verified: {results.social_media.verified_found} accounts found
              </p>
              <div className="platform-grid">
                {results.social_media.platforms?.map((platform, i) => (
                  <div key={i} className={`platform-card ${platform.status}`}>
                    <a href={platform.url} target="_blank" rel="noopener noreferrer">
                      {platform.name} {platform.status === 'found' && '✅'}
                      {platform.status === 'not_found' && '❌'}
                      {platform.status === 'check_manually' && '🔍'}
                    </a>
                  </div>
                ))}
              </div>
            </div>

            {/* Username Search */}
            {results.username_search && (
              <div className="section">
                <h3>🔎 Username: {results.username_search.username}</h3>
                <div className="platform-grid">
                  {results.username_search.sites?.map((site, i) => (
                    <div key={i} className={`platform-card ${site.status}`}>
                      <a href={site.url} target="_blank" rel="noopener noreferrer">
                        {site.name} {site.status === 'found' && '✅'}
                        {site.status === 'not_found' && '❌'}
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Domain Info */}
            <div className="section">
              <h3>🌐 Domain Analysis: {results.domain_info.domain}</h3>
              <div className="domain-links">
                <a href={results.domain_info.whois} target="_blank" rel="noopener noreferrer">
                  WHOIS Lookup →
                </a>
                <a href={results.domain_info.dns_lookup} target="_blank" rel="noopener noreferrer">
                  DNS/MX Records →
                </a>
                <a href={results.domain_info.security_headers} target="_blank" rel="noopener noreferrer">
                  Security Headers →
                </a>
                <a href={results.domain_info.ssl_check} target="_blank" rel="noopener noreferrer">
                  SSL Analysis →
                </a>
              </div>
              {results.domain_info.mx_records && (
                <div className="mx-records">
                  <p><strong>MX Records:</strong></p>
                  <ul>
                    {results.domain_info.mx_records.map((mx, i) => (
                      <li key={i}>{mx}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Google Dorks */}
            <div className="section google-dorks">
              <h3>🔍 Google Dork Queries</h3>
              <p className="detail">Use these advanced search queries to find more info:</p>
              <div className="dork-list">
                {results.google_dorks.dorks?.map((dork, i) => (
                  <div key={i} className="dork-item">
                    <code>{dork}</code>
                    <a 
                      href={`https://www.google.com/search?q=${encodeURIComponent(dork)}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="search-btn"
                    >
                      Search
                    </a>
                  </div>
                ))}
              </div>
            </div>

            <div className="footer-note">
              <p>⚠️ This tool is for educational and ethical OSINT purposes only. Always respect privacy and legal boundaries.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
