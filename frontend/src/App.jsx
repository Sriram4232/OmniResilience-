import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, Package, Zap, X, BrainCircuit, Box } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './index.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

function App() {
  const [inventory, setInventory] = useState([]);
  const [disruptions, setDisruptions] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [agentResult, setAgentResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const invRes = await axios.get(`${API_BASE}/inventory`);
      setInventory(invRes.data.inventory);
      
      const disRes = await axios.get(`${API_BASE}/disruptions`);
      setDisruptions(disRes.data.disruptions);
    } catch (e) {
      console.error("Failed to fetch data", e);
    }
  };

  const runAgent = async (product_id) => {
    setSelectedProduct(product_id);
    setLoading(true);
    setAgentResult(null);
    try {
      const res = await axios.post(`${API_BASE}/analyze`, { product_id });
      setAgentResult(res.data);
    } catch (e) {
      console.error("Failed to run agent", e);
      setAgentResult({ analysis: "Failed to connect to agent.", strategy: {} });
    }
    setLoading(false);
  };

  return (
    <div className="dashboard-container">
      <header>
        <div className="logo">
          <h1>OmniResilience AI</h1>
          <p>Multimodal Merchandising & Supply Chain Agent</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="card" style={{ padding: '0.5rem 1rem', marginBottom: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} color="var(--accent-cyan)" />
            <span>Agent Active</span>
          </div>
        </div>
      </header>

      <div className="grid-layout">
        <div className="main-content">
          <div className="card">
            <h2><Package size={20} /> Inventory Assortment</h2>
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Stock / Reorder</th>
                  <th>Supplier</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map(item => (
                  <tr key={item.product_id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{item.name}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>ID: {item.product_id}</div>
                    </td>
                    <td>{item.category}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '100%', backgroundColor: 'rgba(255,255,255,0.1)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ 
                            width: `${Math.min(100, (item.current_stock / (item.reorder_point * 3)) * 100)}%`, 
                            backgroundColor: item.current_stock <= item.reorder_point ? 'var(--accent-danger)' : 'var(--accent-success)',
                            height: '100%'
                          }}></div>
                        </div>
                        <span>{item.current_stock}</span>
                      </div>
                    </td>
                    <td>{item.supplier}</td>
                    <td>
                      <button className="btn" onClick={() => runAgent(item.product_id)}>
                         Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="sidebar">
          <div className="card">
            <h2><AlertTriangle size={20} color="var(--accent-warning)" /> Live Disruptions</h2>
            <div className="disruptions-feed">
              {disruptions.map((d, i) => (
                <div key={i} className={`disruption-item ${d.severity.toLowerCase()}`}>
                  <div className="disruption-header">
                    <span>{d.source}</span>
                    <span>{new Date(d.timestamp).toLocaleDateString()}</span>
                  </div>
                  <div className="disruption-content">{d.content}</div>
                </div>
              ))}
              {disruptions.length === 0 && <p>No active disruptions.</p>}
            </div>
          </div>
        </div>
      </div>

      {selectedProduct && (
        <div className="agent-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2><BrainCircuit size={24} color="var(--accent-cyan)" /> Agent Reasoning Engine</h2>
              <button className="close-btn" onClick={() => setSelectedProduct(null)}><X size={24} /></button>
            </div>
            
            {loading ? (
              <div className="agent-loader">
                <div className="spinner"></div>
                <p>Analyzing multimodal supply chain signals & computing optimal markdown strategies...</p>
              </div>
            ) : agentResult ? (
              <div className="agent-results">
                <div className="card" style={{ marginBottom: '1rem', background: 'rgba(0,0,0,0.2)' }}>
                  <h3 style={{ marginTop: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}>Risk Analysis</h3>
                  <div style={{ lineHeight: 1.6, fontSize: '0.95rem' }} className="markdown-container">
                    <ReactMarkdown>{agentResult.analysis}</ReactMarkdown>
                  </div>
                </div>
                
                {agentResult.strategy.error ? (
                   <p style={{ color: 'var(--accent-danger)' }}>{agentResult.strategy.error}</p>
                ) : (
                  <div>
                    <h3 style={{ margin: '1.5rem 0 0 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Zap size={20} color="var(--accent-warning)" /> Actionable Strategy
                    </h3>
                    <div className="strategy-grid">
                      <div className="strategy-card">
                        <div className="strategy-label">Recommended Action</div>
                        <div className="strategy-value">{agentResult.strategy.recommended_action}</div>
                      </div>
                      <div className="strategy-card">
                        <div className="strategy-label">Replenishment Adjustment</div>
                        <div className="strategy-value">{agentResult.strategy.replenishment_order_adjustment}</div>
                      </div>
                      <div className="strategy-card">
                        <div className="strategy-label">Markdown Timing</div>
                        <div className="strategy-value">{agentResult.strategy.markdown_timing}</div>
                      </div>
                      <div className="strategy-card">
                        <div className="strategy-label">Expected Margin Impact</div>
                        <div className="strategy-value">{agentResult.strategy.expected_margin_impact}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
