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
            <div className="progress-bar"><div className="progress-fill" style={{width: `${progress}%`}}></div></div>
            <p className="progress-text">Deep scanning databases... {Math.round(progress)}%</p>
          </div>
        )}
        
        {error && <div className="error">{error}</div>}
        {results && (
          <div className="results">
            <div className="results-header"><h2>🎯 Investigation Report</h2>{results.email_results && <p className="target-email">{results.email_results.email}</p>}{results.name_results && <p className="target-name">{results.name_results.full_name}</p>}</div>
            
            {/* NAME RESULTS */}
            {results.name_results && (<>
              {results.name_results.email_match && (<div className="section"><h3>🔗 Email-Name Match</h3><div className={`confidence-badge ${results.name_results.email_match.confidence.toLowerCase()}`}>{results.name_results.email_match.confidence} Confidence</div><ul>{results.name_results.email_match.details.map((detail, i) => (<li key={i}>{detail}</li>))}</ul></div>)}
              
              {results.name_results.username_investigations && (<div className="section"><h3>🔤 Username Analysis</h3><div className="username-analysis-grid">{results.name_results.username_investigations.map((investigation, i) => (<div key={i} className="username-analysis-card"><div className="username-header"><span className="username-text">{investigation.username}</span><div className={`probability-mini ${investigation.confidence.toLowerCase()}`}>{investigation.probability}%</div></div><div className="confidence-bar"><div className={`confidence-fill ${investigation.confidence.toLowerCase()}`} style={{width: `${investigation.probability}%`}}></div></div><p className="confidence-text">{investigation.confidence} Confidence</p><p className="platforms-found">Found: {investigation.platforms_found}/{investigation.platforms_checked}</p><div className="platform-mini-grid">{investigation.details.filter(d => d.status === 'found').map((detail, j) => (<a key={j} href={detail.url} target="_blank" rel="noopener noreferrer" className="platform-mini">{detail.platform} ✅</a>))}</div></div>))}</div></div>)}
              
              {results.name_results.potential_emails && (<div className="section"><h3>📧 Potential Emails</h3><p className="detail">{results.name_results.potential_emails.note}</p><div className="email-list">{results.name_results.potential_emails.patterns.map((emailAddr, i) => (<div key={i} className="email-item">{emailAddr}</div>))}</div></div>)}
              
              {results.name_results.social_media && (<div className="section"><h3>📱 Social Media</h3><p className="detail">{results.name_results.social_media.note}</p><div className="platform-grid">{results.name_results.social_media.platforms.map((platform, i) => (<div key={i} className="platform-card"><a href={platform.url} target="_blank" rel="noopener noreferrer">{platform.name}</a><p className="platform-desc">{platform.description}</p></div>))}</div></div>)}
              
              {results.name_results.professional && (<div className="section"><h3>💼 Professional</h3><div className="platform-grid">{results.name_results.professional.map((site, i) => (<div key={i} className="platform-card"><a href={site.url} target="_blank" rel="noopener noreferrer">{site.name}</a><p className="platform-desc">{site.type}</p></div>))}</div></div>)}
              
              {results.name_results.dark_web && (<div className="section dark-web"><h3>🕵️ Dark Web</h3><p className="detail">{results.name_results.dark_web.note}</p><div className="platform-grid">{results.name_results.dark_web.search_engines.map((engine, i) => (<div key={i} className="platform-card"><a href={engine.url} target="_blank" rel="noopener noreferrer">{engine.name}</a><p className="platform-desc">{engine.description}</p></div>))}</div></div>)}
              
              {results.name_results.public_records && (<div className="section"><h3>📋 Public Records</h3><p className="warning">{results.name_results.public_records.warning}</p>{results.name_results.public_records.verified_count > 0 && (<div className="stats success">✅ Found results in {results.name_results.public_records.verified_count} databases</div>)}<div className="platform-grid">{results.name_results.public_records.databases.map((db, i) => (<div key={i} className={`platform-card verification-${db.verification_status || 'not_checked'}`}><div className="verification-header"><span className="status-icon">{db.status_icon || '⏳'}</span><span className="status-text">{db.verification_status === 'found' && 'Results Found'}{db.verification_status === 'not_found' && 'No Results'}{db.verification_status === 'check_manually' && 'Check Manually'}{db.verification_status === 'error' && 'Error'}{(!db.verification_status || db.verification_status === 'not_checked') && 'Not Checked'}</span></div><a href={db.url} target="_blank" rel="noopener noreferrer">{db.name}</a><p className="platform-desc">{db.description}</p></div>))}</div></div>)}
              
              {results.name_results.google_dorks && (<div className="section google-dorks"><h3>🔍 Google Dorks (Name)</h3><p className="detail">{results.name_results.google_dorks.note}</p>{results.name_results.google_dorks.regions && (<div className="stats">🇬🇧 UK/EU: {results.name_results.google_dorks.regions.uk_eu_count} | 🇺🇸 US: {results.name_results.google_dorks.regions.us_count}</div>)}<div className="dork-list">{results.name_results.google_dorks.dorks.map((dork, i) => (<div key={i} className={`dork-item priority-${dork.priority}`}><div className="dork-header"><span className={`region-badge ${dork.region.toLowerCase()}`}>{dork.region}</span><span className={`priority-badge ${dork.priority}`}>{dork.priority}</span>{dork.result_count && <span className="result-count">📊 {dork.result_count} results</span>}</div><code>{dork.query}</code><p className="dork-desc">{dork.description}</p><a href={`https://www.google.com/search?q=${encodeURIComponent(dork.query)}`} target="_blank" rel="noopener noreferrer" className="search-btn">Search</a></div>))}</div></div>)}
            </>)}

            {/* EMAIL RESULTS */}
            {results.email_results && (<>
              {results.email_results.reputation && !results.email_results.reputation.error && (<div className="section reputation"><h3>📊 Reputation</h3><div className={`reputation-badge ${results.email_results.reputation.reputation}`}>{results.email_results.reputation.reputation?.toUpperCase() || 'UNKNOWN'}</div>{results.email_results.reputation.suspicious && (<p className="warning">⚠️ Suspicious</p>)}<p>References: {results.email_results.reputation.references || 0}</p></div>)}
              
              {results.email_results.breaches && (<div className="section"><h3>🔒 Data Breaches (Multiple Sources)</h3><div className="breach-sources">{results.email_results.breaches.details.map((source, i) => (<div key={i} className="source-item"><strong>{source.source}:</strong> {source.status}{source.count > 0 && <span> ({source.count} breaches)</span>}</div>))}</div>{results.email_results.breaches.found && results.email_results.breaches.breaches_found.length > 0 ? (<div className="breach-list">{results.email_results.breaches.breaches_found.map((breach, i) => (<div key={i} className="breach-item"><h4>{breach.name}</h4><p className="breach-date">{breach.date}</p><p className="breach-data">{breach.data?.join(', ')}</p></div>))}</div>) : (<p className="success">✅ No breaches found</p>)}</div>)}
              
              {results.email_results.paste_sites && (<div className="section dark-web"><h3>📋 Paste Sites</h3>{results.email_results.paste_sites.total_found > 0 ? (<><p className="warning">⚠️ Found in {results.email_results.paste_sites.total_found} pastes!</p><div className="paste-list">{results.email_results.paste_sites.found_pastes.map((paste, i) => (<div key={i} className="paste-item"><a href={paste.url} target="_blank" rel="noopener noreferrer">{paste.title}</a><p className="paste-time">{new Date(paste.time * 1000).toLocaleString()}</p></div>))}</div></>) : (<p className="success">✅ No pastes found</p>)}</div>)}
              
              {results.email_results.dark_web_mentions && (<div className="section dark-web"><h3>🕵️ Dark Web & Leak Databases</h3><p className="detail">{results.email_results.dark_web_mentions.note}</p><h4 style={{color: '#667eea', marginBottom: '10px'}}>Search Engines</h4><div className="platform-grid">{results.email_results.dark_web_mentions.search_engines.map((engine, i) => (<div key={i} className="platform-card"><a href={engine.url} target="_blank" rel="noopener noreferrer">{engine.name}</a><p className="platform-desc">{engine.description}</p></div>))}</div><h4 style={{color: '#667eea', marginTop: '20px', marginBottom: '10px'}}>Leak Databases</h4><div className="platform-grid">{results.email_results.dark_web_mentions.leak_databases.map((db, i) => (<div key={i} className="platform-card"><a href={db.url} target="_blank" rel="noopener noreferrer">{db.name}</a><p className="platform-desc">{db.note}</p></div>))}</div></div>)}
              
              {results.email_results.social_media && (<div className="section"><h3>📱 Social Media</h3><p className="stats">Verified: {results.email_results.social_media.verified_found}</p><div className="platform-grid">{results.email_results.social_media.platforms?.map((platform, i) => (<div key={i} className={`platform-card ${platform.status}`}><a href={platform.url} target="_blank" rel="noopener noreferrer">{platform.name} {platform.status === 'found' && '✅'}{platform.status === 'not_found' && '❌'}{platform.status === 'check_manually' && '🔍'}</a></div>))}</div></div>)}
              
              {results.email_results.google_dorks && (<div className="section google-dorks"><h3>🔍 Google Dorks (Email)</h3><p className="detail">{results.email_results.google_dorks.note}</p>{results.email_results.google_dorks.regions && (<div className="stats">🇬🇧 UK/EU: {results.email_results.google_dorks.regions.uk_eu_count} | 🇺🇸 US: {results.email_results.google_dorks.regions.us_count}</div>)}<div className="dork-list">{results.email_results.google_dorks.dorks.map((dork, i) => (<div key={i} className={`dork-item priority-${dork.priority}`}><div className="dork-header"><span className={`region-badge ${dork.region.toLowerCase()}`}>{dork.region}</span><span className={`priority-badge ${dork.priority}`}>{dork.priority}</span>{dork.result_count && <span className="result-count">📊 {dork.result_count} results</span>}</div><code>{dork.query}</code><p className="dork-desc">{dork.description}</p><a href={`https://www.google.com/search?q=${encodeURIComponent(dork.query)}`} target="_blank" rel="noopener noreferrer" className="search-btn">Search</a></div>))}</div></div>)}
            </>)}

            <div className="footer-note"><p>⚠️ Educational purposes only. Respect privacy and legal boundaries.</p></div>
          </div>
        )}
      </div>
    </div>
  );
}
export default App;
