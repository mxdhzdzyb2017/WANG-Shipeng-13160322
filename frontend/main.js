// API基础URL
const API_BASE = 'http://localhost:5001/api';

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    checkSystemStatus();
    showLatestData();
    
    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('gdeltDateInput').value = today;
});

// 检查系统状态
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        // 保存状态供其他函数使用
        window.lastSystemStatus = data;
        
        let statusHtml = '';
        if (!data.initialized) {
            statusHtml = `<p class="error">❌ ${t('predictor_not_initialized')}</p>`;
        } else {
            statusHtml = `
                <div class="status-info">
                    <p>✅ ${t('system_ready')}</p>
                    <p>📅 ${t('data_range')}：${data.date_range.start || t('none')} ${t('to')} ${data.date_range.end || t('none')}</p>
                    <p>📊 ${t('current_progress')}：${data.current_index}/${data.total_dates}</p>
                    <p>💱 ${t('available_pairs')}：${data.currencies.join(', ')}</p>
                </div>
            `;
        }
        
        document.getElementById('systemStatus').innerHTML = statusHtml;
    } catch (error) {
        document.getElementById('systemStatus').innerHTML = 
            `<p class="error">❌ ${t('cannot_connect')}</p>`;
    }
}

// 显示最新数据
async function showLatestData() {
    try {
        const response = await fetch(`${API_BASE}/get-latest-data`);
        const data = await response.json();
        
        if (data.error) {
            return;
        }
        
        let html = `<h3>${t('latest_data')}</h3>`;
        
        if (data.latest_date) {
            html += `<p>${t('latest_date')}：${data.latest_date}</p>`;
        }
        
        // 显示汇率
        if (Object.keys(data.forex).length > 0) {
            html += `<h4>${t('exchange_rate')}：</h4><div class="data-grid">`;
            for (const [pair, info] of Object.entries(data.forex)) {
                html += `<div class="data-item">${pair}: ${info.value.toFixed(4)}</div>`;
            }
            html += '</div>';
        }
        
        // 显示国债
        if (Object.keys(data.bonds).length > 0) {
            html += `<h4>${t('bond_yield')}：</h4><div class="data-grid">`;
            for (const [country, info] of Object.entries(data.bonds)) {
                const countryName = country === 'CN' ? t('china_bond') : 
                                  country === 'US' ? t('us_bond') : 
                                  country === 'UK' ? t('uk_bond') : country;
                html += `<div class="data-item">${countryName}: ${info.value.toFixed(2)}%</div>`;
            }
            html += '</div>';
        }
        
        document.getElementById('latestData').innerHTML = html;
    } catch (error) {
        console.error('获取最新数据失败:', error);
    }
}

// 更新汇率和国债数据
document.getElementById('updateForexBtn').addEventListener('click', async function() {
    const btn = this;
    const resultDiv = document.getElementById('forexUpdateResult');
    
    btn.disabled = true;
    btn.querySelector('[data-i18n]').textContent = t('updating');
    resultDiv.innerHTML = `<p class="info">${t('getting_latest')}</p>`;
    
    try {
        const response = await fetch(`${API_BASE}/update-forex-data`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="success-box">
                    <h4>✅ ${t('update_success')}</h4>
                    <pre>${data.message}</pre>
                    <p>${t('total_data_days')}：${data.total_dates}</p>
                </div>
            `;
            
            // 刷新系统状态和最新数据
            checkSystemStatus();
            showLatestData();
        } else {
            resultDiv.innerHTML = `<p class="error">❌ ${t('update_failed')}：${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">❌ ${t('request_failed')}：${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.querySelector('[data-i18n]').textContent = t('update_forex');
    }
});

// 更新GDELT数据
document.getElementById('updateGdeltBtn').addEventListener('click', async function() {
    const btn = this;
    const dateInput = document.getElementById('gdeltDateInput');
    const resultDiv = document.getElementById('gdeltUpdateResult');
    
    if (!dateInput.value) {
        alert(t('please_select_date'));
        return;
    }
    
    btn.disabled = true;
    btn.querySelector('[data-i18n]').textContent = t('updating');
    resultDiv.innerHTML = `<p class="info">${t('downloading_gdelt')}</p>`;
    
    try {
        const response = await fetch(`${API_BASE}/download-gdelt`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({date: dateInput.value})
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="success-box">
                    <h4>✅ ${t('update_success')}</h4>
                    <pre>${data.message}</pre>
                </div>
            `;
            
            // 刷新系统状态
            checkSystemStatus();
        } else {
            resultDiv.innerHTML = `<p class="error">❌ ${t('update_failed')}：${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">❌ ${t('request_failed')}：${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.querySelector('[data-i18n]').textContent = t('update_gdelt');
    }
});

// 预测下一天
document.getElementById('predictBtn').addEventListener('click', async function() {
    try {
        const response = await fetch(`${API_BASE}/predict-next`);
        const data = await response.json();
        
        if (data.error) {
            alert(t('prediction_error') + '：' + data.error);
            return;
        }
        
        if (data.finished) {
            document.getElementById('resultsContainer').innerHTML = 
                `<p class="info">${t('all_predicted')}</p>`;
            return;
        }
        
        displayPrediction(data);
        updatePredictionStats();
    } catch (error) {
        alert(t('prediction_error') + '：' + error.message);
    }
});

// 批量预测
document.getElementById('predictMultipleBtn').addEventListener('click', async function() {
    const days = parseInt(document.getElementById('daysInput').value);
    
    if (days < 1 || days > 30) {
        alert(t('please_enter_days'));
        return;
    }
    
    const btn = this;
    btn.disabled = true;
    btn.querySelector('[data-i18n]').textContent = t('predicting');
    
    try {
        const response = await fetch(`${API_BASE}/predict-multiple`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({days: days})
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(t('prediction_error') + '：' + data.error);
            return;
        }
        
        if (data.results && data.results.length > 0) {
            // 显示所有预测结果
            data.results.forEach(result => {
                displayPrediction(result);
            });
            
            updatePredictionStats();
            
            if (data.results.length < days) {
                alert(`${t('can_only_predict')} ${data.results.length} ${t('days_insufficient')}`);
            }
        } else {
            alert(t('no_predictable_data'));
        }
    } catch (error) {
        alert(t('batch_predict_failed') + '：' + error.message);
    } finally {
        btn.disabled = false;
        btn.querySelector('[data-i18n]').textContent = t('batch_predict');
    }
});

// 重置
document.getElementById('resetBtn').addEventListener('click', async function() {
    if (!confirm(t('confirm_reset'))) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('resultsContainer').innerHTML = '';
            document.getElementById('predictionStats').innerHTML = '';
            checkSystemStatus();
            alert(t('history_reset'));
        }
    } catch (error) {
        alert(t('reset_failed') + '：' + error.message);
    }
});

// 显示预测结果
function displayPrediction(data) {
    if (!data || !data.pairs) return;
    
    let html = `
        <div class="prediction-result">
            <h3>📅 ${data.date}${data.is_future_prediction ? ' (未来预测)' : ''}</h3>
            <table>
                <thead>
                    <tr>
                        <th>${t('currency_pair')}</th>
                        <th>${t('prediction')}</th>
                        ${!data.is_future_prediction ? `
                        <th>${t('actual')}</th>
                        <th>${t('result')}</th>` : ''}
                        <th>${t('current_price')}</th>
                        ${!data.is_future_prediction ? `<th>${t('next_price')}</th>
                        <th>${t('change')}</th>` : ''}
                        <th>${t('accuracy')}</th>
                    </tr>
                </thead>
                <tbody>`;
    
    data.pairs.forEach(pair => {
        if (data.is_future_prediction) {
            // 未来预测的显示
            html += `
                <tr>
                    <td>${pair.name}</td>
                    <td class="pred-${pair.pred}">${pair.pred === 1 ? '📈 ' + t('rise') : pair.pred === 0 ? '📉 ' + t('fall') : '-'}</td>
                    <td>${pair.close ? pair.close.toFixed(4) : '-'}</td>
                    <td>${pair.acc !== null ? (pair.acc * 100).toFixed(1) + '%' : '-'}</td>
                </tr>`;
        } else {
            // 历史数据的显示
            if (pair.close && pair.next_close) {
                const change = pair.next_close - pair.close;
                const changePercent = (change / pair.close * 100).toFixed(3);
                const isCorrect = pair.pred === pair.real;
                
                html += `
                    <tr class="${isCorrect ? 'correct' : 'incorrect'}">
                        <td>${pair.name}</td>
                        <td class="pred-${pair.pred}">${pair.pred === 1 ? '📈 ' + t('rise') : pair.pred === 0 ? '📉 ' + t('fall') : '-'}</td>
                        <td class="real-${pair.real}">${pair.real === 1 ? '📈 ' + t('rise') : pair.real === 0 ? '📉 ' + t('fall') : '-'}</td>
                        <td>${isCorrect ? '✅' : '❌'}</td>
                        <td>${pair.close.toFixed(4)}</td>
                        <td>${pair.next_close.toFixed(4)}</td>
                        <td class="${change >= 0 ? 'positive' : 'negative'}">
                            ${change >= 0 ? '+' : ''}${change.toFixed(4)} 
                            (${changePercent >= 0 ? '+' : ''}${changePercent}%)
                        </td>
                        <td>${pair.acc !== null ? (pair.acc * 100).toFixed(1) + '%' : '-'}</td>
                    </tr>`;
            }
        }
    });
    
    html += `
                </tbody>
            </table>
        </div>`;
    
    const container = document.getElementById('resultsContainer');
    
    // 保存当前滚动位置
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    container.innerHTML = html + container.innerHTML;
    
    // 恢复滚动位置
    window.scrollTo(0, scrollTop);
}

// 更新预测统计
async function updatePredictionStats() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.accuracy && Object.keys(data.accuracy).length > 0) {
            let html = `<h3>${t('prediction_stats')}</h3><div class="stats-grid">`;
            
            for (const [curr, acc] of Object.entries(data.accuracy)) {
                const rate = (acc.rate * 100).toFixed(1);
                const color = rate >= 60 ? 'good' : rate >= 50 ? 'medium' : 'poor';
                
                html += `
                    <div class="stat-item ${color}">
                        <div class="stat-name">${curr}</div>
                        <div class="stat-value">${rate}%</div>
                        <div class="stat-detail">${acc.correct}/${acc.total}</div>
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('predictionStats').innerHTML = html;
        }
    } catch (error) {
        console.error('更新统计失败:', error);
    }
}