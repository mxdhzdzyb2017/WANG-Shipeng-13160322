// 交易相关功能
let tradingSettings = {};

// 加载交易设置
async function loadTradingSettings() {
    try {
        const response = await fetch(`${API_BASE}/trading/settings`);
        tradingSettings = await response.json();
        
        // 更新UI
        document.getElementById('baseCurrency').value = tradingSettings.base_currency || 'USD';
        document.getElementById('initialBalance').value = tradingSettings.initial_balance || 10000;
        document.getElementById('autoTradeToggle').checked = tradingSettings.auto_trade_enabled || false;
        document.getElementById('autoTradeTime').value = tradingSettings.auto_trade_time || '09:00';
        
        // 显示货币持有量
        displayCurrencyHoldings();
        
        // 生成分配网格
        generateAllocationGrid();
        
        // 更新性能统计
        updatePerformanceStats();
        
        // 加载交易历史
        loadTradeHistory();
        
    } catch (error) {
        console.error('加载交易设置失败:', error);
    }
}

// 显示货币持有量
function displayCurrencyHoldings() {
    const holdings = tradingSettings.currency_holdings || {};
    let html = '<div class="currency-holdings-grid">';
    
    for (const [currency, amount] of Object.entries(holdings)) {
        html += `
            <div class="currency-holding-item">
                <span class="currency-name">${currency}</span>
                <span class="currency-amount">${amount.toFixed(2)}</span>
            </div>
        `;
    }
    
    html += '</div>';
    document.getElementById('currencyHoldings').innerHTML = html;
}

// 生成资金分配网格
function generateAllocationGrid() {
    const grid = document.getElementById('allocationGrid');
    const allocations = tradingSettings.currency_allocations || {};
    const reverseModels = tradingSettings.reverse_models || [];
    
    let html = '';
    for (const [currency, percentage] of Object.entries(allocations)) {
        const isReversed = reverseModels.includes(currency);
        
        // 获取该货币对的准确率
        let accuracy = 0;
        let hasHistory = false;
        
        // 首先检查 tradingSettings 中的准确率历史
        if (tradingSettings.accuracy_history && tradingSettings.accuracy_history[currency]) {
            const historyInfo = tradingSettings.accuracy_history[currency];
            if (historyInfo.total > 0) {
                accuracy = historyInfo.rate * 100;
                hasHistory = true;
            }
        }
        
        // 如果没有历史记录，再检查系统状态
        if (!hasHistory && window.lastSystemStatus && window.lastSystemStatus.accuracy && window.lastSystemStatus.accuracy[currency]) {
            accuracy = window.lastSystemStatus.accuracy[currency].rate * 100;
        }
        
        // 获取交易次数信息
        const tradeCount = tradingSettings.accuracy_history && tradingSettings.accuracy_history[currency] 
            ? tradingSettings.accuracy_history[currency].total 
            : 0;
        
        // 判断是否会自动反向
        const willAutoReverse = accuracy < 50 && tradeCount >= 10;
        
        html += `
            <div class="allocation-item ${willAutoReverse ? 'auto-reverse' : ''}">
                <div class="allocation-header">
                    <span>${currency}</span>
                    <span class="accuracy-badge ${accuracy >= 60 ? 'good' : accuracy >= 50 ? 'medium' : 'poor'}">
                        ${accuracy.toFixed(1)}% ${tradeCount > 0 ? `(${tradeCount})` : ''}
                    </span>
                </div>
                <div>
                    <input type="number" id="alloc_${currency}" value="${percentage}" min="0" max="100" step="0.01">%
                    <button class="reverse-btn ${isReversed ? 'active' : ''}" 
                            onclick="toggleReverse('${currency}')" 
                            title="${isReversed ? t('current_reverse') : t('current_normal')}">
                        ${isReversed ? t('reverse') : t('normal')}
                    </button>
                </div>
                ${tradeCount < 10 ? 
                    `<div class="info-text">${t('initial_stage')}</div>` : 
                    willAutoReverse ? `<div class="warning-text">${t('auto_reverse_hint')}</div>` : ''}
            </div>
        `;
    }
    grid.innerHTML = html;
}

// 切换反向交易
async function toggleReverse(currency) {
    try {
        const response = await fetch(`${API_BASE}/trading/toggle-reverse/${currency}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            // 重新加载设置
            loadTradingSettings();
            
            // 更新预测统计显示
            if (typeof updatePredictionStats === 'function') {
                updatePredictionStats();
            }
        }
    } catch (error) {
        console.error('切换反向交易失败:', error);
    }
}

// 保存设置
async function saveSettings() {
    try {
        // 收集分配数据
        const allocations = {};
        let totalAllocation = 0;
        
        for (const currency of Object.keys(tradingSettings.currency_allocations)) {
            const value = parseFloat(document.getElementById(`alloc_${currency}`).value) || 0;
            allocations[currency] = value;
            totalAllocation += value;
        }
        
        // 检查总和是否为100%
        if (Math.abs(totalAllocation - 100) > 0.01) {
            alert(t('allocation_must_be_100').replace('{total}', totalAllocation.toFixed(2)));
            return;
        }
        
        const settings = {
            base_currency: document.getElementById('baseCurrency').value,
            initial_balance: parseFloat(document.getElementById('initialBalance').value),
            currency_allocations: allocations,
            auto_trade_enabled: document.getElementById('autoTradeToggle').checked,
            auto_trade_time: document.getElementById('autoTradeTime').value
        };
        
        const response = await fetch(`${API_BASE}/trading/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            alert(t('settings_saved'));
            loadTradingSettings();
        }
    } catch (error) {
        console.error('保存设置失败:', error);
        alert(t('save_settings_failed'));
    }
}

// 重置投资组合
async function resetPortfolio() {
    if (!confirm(t('confirm_reset_portfolio'))) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/trading/reset-portfolio`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert(t('portfolio_reset'));
            loadTradingSettings();
        }
    } catch (error) {
        console.error('重置投资组合失败:', error);
        alert(t('reset_portfolio_failed'));
    }
}

// 更新性能统计
function updatePerformanceStats() {
    const stats = tradingSettings;
    
    let html = `
        <div class="stat-card">
            <h4>${t('initial_balance')}</h4>
            <div class="value">${(stats.initial_balance || 0).toFixed(2)} ${stats.base_currency || 'USD'}</div>
        </div>
        <div class="stat-card">
            <h4>${t('total_profit')}</h4>
            <div class="value ${stats.total_profit >= 0 ? 'positive' : 'negative'}">
                ${stats.total_profit >= 0 ? '+' : ''}${(stats.total_profit || 0).toFixed(2)}
                <span style="font-size: 14px; font-weight: normal;">
                    (${stats.total_profit && stats.initial_balance ? 
                        ((stats.total_profit / stats.initial_balance * 100).toFixed(2) + '%') : 
                        '0.00%'})
                </span>
            </div>
        </div>
        <div class="stat-card">
            <h4>${t('total_trades')}</h4>
            <div class="value">${stats.total_trades || 0}</div>
        </div>
    `;
    
    document.getElementById('performanceStats').innerHTML = html;
}

// 加载交易历史
async function loadTradeHistory() {
    try {
        const response = await fetch(`${API_BASE}/trading/history`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const trades = await response.json();
        
        let html = '';
        if (Array.isArray(trades) && trades.length > 0) {
            // 只显示最近20条记录
            const recentTrades = trades.slice(-20).reverse();
            
            recentTrades.forEach(trade => {
                const tradeClass = trade.prediction === 'BUY' ? 'buy' : 'sell';
                html += `
                    <div class="trade-item ${tradeClass}">
                        <span class="trade-date">${trade.date}</span>
                        <span class="trade-pair">${trade.pair} ${trade.prediction}</span>
                        <span class="trade-amount">${trade.amount.toFixed(2)} ${trade.from_currency} → ${trade.received.toFixed(2)} ${trade.to_currency}</span>
                        <span class="trade-price">@${trade.price.toFixed(4)}</span>
                        ${trade.is_reversed ? `<span class="reversed-badge">${t('reverse')}</span>` : ''}
                        <span class="accuracy-info">${(trade.accuracy * 100).toFixed(1)}%</span>
                    </div>
                `;
            });
        } else {
            html = `<p class="no-trades">${t('no_trades_yet')}</p>`;
        }
        
        document.getElementById('tradeHistory').innerHTML = html;
    } catch (error) {
        console.error('加载交易历史失败:', error);
        // 显示无交易记录而不是错误信息
        document.getElementById('tradeHistory').innerHTML = `<p class="no-trades">${t('no_trades_yet')}</p>`;
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadTradingSettings();
    
    // 每30秒刷新一次交易数据
    setInterval(() => {
        loadTradingSettings();
    }, 30000);
});

// 保存系统状态供其他函数使用
window.lastSystemStatus = null;