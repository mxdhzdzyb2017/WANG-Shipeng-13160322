// 语言翻译字典
const translations = {
    zh: {
        // 页面标题和主要标题
        title: "外汇市场量化交易项目",
        system_status: "系统状态",
        data_update: "数据更新（通过API获取）",
        predict_trade: "预测交易",
        
        // 按钮文本
        update_forex: "更新汇率和国债数据",
        update_gdelt: "更新GDELT新闻数据",
        predict_next: "预测下一天",
        batch_predict: "批量预测",
        reset_history: "重置预测历史",
        manual_input: "手动输入历史数据",
        
        // 标签和提示
        batch_days: "批量预测天数：",
        currency_pairs: "货币对：USD_CNY, USD_GBP, CNY_USD, GBP_CNY, GBP_USD, CNY_GBP",
        connecting: "正在连接服务器...",
        
        // 系统状态消息
        predictor_not_initialized: "预测器未初始化",
        system_ready: "系统已就绪",
        data_range: "数据范围",
        current_progress: "当前进度",
        available_pairs: "可用货币对",
        cannot_connect: "无法连接到服务器",
        
        // 数据显示
        latest_data: "最新数据",
        latest_date: "最新日期",
        exchange_rate: "汇率",
        bond_yield: "国债收益率",
        
        // 更新消息
        updating: "更新中...",
        update_success: "更新成功！",
        update_failed: "更新失败",
        getting_latest: "正在获取最新数据，请稍候...",
        downloading_gdelt: "正在下载GDELT数据，请稍候...",
        total_data_days: "总数据天数",
        request_failed: "请求失败",
        
        // 预测相关
        prediction_error: "预测错误",
        all_predicted: "已全部预测完毕，请重置后重新开始。",
        predicting: "预测中...",
        please_enter_days: "请输入1-30之间的天数",
        can_only_predict: "只能预测",
        days_insufficient: "天（数据不足）",
        no_predictable_data: "没有可预测的数据",
        batch_predict_failed: "批量预测失败",
        
        // 预测结果表头
        currency_pair: "货币对",
        prediction: "预测",
        actual: "实际",
        result: "结果",
        current_price: "当前价",
        next_price: "次日价",
        change: "变化",
        accuracy: "准确率",
        
        // 预测结果
        rise: "涨",
        fall: "跌",
        
        // 统计
        prediction_stats: "预测统计",
        
        // 确认和提示
        confirm_reset: "确定要重置预测历史吗？",
        history_reset: "预测历史已重置",
        reset_failed: "重置失败",
        please_select_date: "请选择日期",
        
        // data_input.html 相关
        manual_data_title: "手动输入历史数据",
        select_date: "选择日期：",
        load_date_data: "加载该日期数据",
        back_to_home: "返回主页",
        forex_data: "汇率数据",
        bond_data: "国债收益率数据 (%)",
        news_data: "新闻数据",
        china_news_count: "中国新闻数量",
        china_news_tone: "中国新闻情绪",
        us_news_count: "美国新闻数量",
        us_news_tone: "美国新闻情绪",
        uk_news_count: "英国新闻数量",
        uk_news_tone: "英国新闻情绪",
        save_data: "保存数据",
        view_existing: "查看已有数据日期",
        existing_dates: "已有数据日期",
        data_save_success: "数据保存成功！",
        save_failed: "保存失败",
        data_load_success: "数据加载成功",
        no_data_for_date: "该日期没有数据",
        load_failed: "加载失败",
        total_days: "共有",
        days_of_data: "天的数据",
        data_completeness: "数据完整性",
        complete: "完整",
        incomplete: "不完整",
        no_data_yet: "暂无数据",
        get_dates_failed: "获取日期列表失败",
        china_bond: "中国国债",
        us_bond: "美国国债",
        uk_bond: "英国国债",
        
        // 交易相关
        trading_settings: "交易设置",
        initial_balance: "初始资金",
        current_balance: "当前余额",
        allocation_settings: "资金分配设置 (%)",
        auto_trade: "自动交易",
        auto_trade_time: "自动交易时间",
        save_settings: "保存设置",
        performance_stats: "交易表现",
        recent_trades: "最近交易",
        total_profit: "总盈亏",
        win_rate: "胜率",
        total_trades: "总交易次数",
        winning_trades: "盈利次数",
        allocation_must_be_100: "分配比例总和必须为100%！当前总和：{total}%",
        settings_saved: "设置已保存",
        save_settings_failed: "保存设置失败",
        base_currency: "基础货币",
        currency_holdings: "货币持有量",
        allocation_hint: "根据模型准确率自动调整交易金额，准确率低于50%的货币对不进行交易",
        portfolio_value: "组合价值",
        reset_portfolio: "重置投资组合",
        confirm_reset_portfolio: "确定要重置投资组合吗？所有货币将重置为初始状态",
        portfolio_reset: "投资组合已重置",
        reset_portfolio_failed: "重置投资组合失败",

        normal : "正常",
        reverse: "反向",
        current_normal: "当前：正常交易",
        current_reverse: "当前：反向交易",
        initial_stage: "初始阶段：保守交易模式",
        auto_reverse_hint: "准确率低于50%，将自动反向交易",
        no_trades_yet: "暂无交易记录",
        load_history_failed: "加载交易历史失败",
    },
    
    en: {
        // Page titles and main headings
        title: "Forex Quantitative Trading Project",
        system_status: "System Status",
        data_update: "Data Update (via API)",
        predict_trade: "Prediction Trading",
        
        // Button texts
        update_forex: "Update Forex & Bonds Data",
        update_gdelt: "Update GDELT News Data",
        predict_next: "Predict Next Day",
        batch_predict: "Batch Predict",
        reset_history: "Reset Prediction History",
        manual_input: "Manual Data Input",
        
        // Labels and hints
        batch_days: "Batch Prediction Days: ",
        currency_pairs: "Currency Pairs: USD_CNY, USD_GBP, CNY_USD, GBP_CNY, GBP_USD, CNY_GBP",
        connecting: "Connecting to server...",
        
        // System status messages
        predictor_not_initialized: "Predictor not initialized",
        system_ready: "System Ready",
        data_range: "Data Range",
        current_progress: "Current Progress",
        available_pairs: "Available Pairs",
        cannot_connect: "Cannot connect to server",
        
        // Data display
        latest_data: "Latest Data",
        latest_date: "Latest Date",
        exchange_rate: "Exchange Rate",
        bond_yield: "Bond Yield",
        
        // Update messages
        updating: "Updating...",
        update_success: "Update Successful!",
        update_failed: "Update Failed",
        getting_latest: "Getting latest data, please wait...",
        downloading_gdelt: "Downloading GDELT data, please wait...",
        total_data_days: "Total Data Days",
        request_failed: "Request Failed",
        
        // Prediction related
        prediction_error: "Prediction Error",
        all_predicted: "All predictions completed. Please reset to start again.",
        predicting: "Predicting...",
        please_enter_days: "Please enter days between 1-30",
        can_only_predict: "Can only predict",
        days_insufficient: "days (insufficient data)",
        no_predictable_data: "No predictable data",
        batch_predict_failed: "Batch prediction failed",
        
        // Prediction result headers
        currency_pair: "Currency Pair",
        prediction: "Prediction",
        actual: "Actual",
        result: "Result",
        current_price: "Current Price",
        next_price: "Next Price",
        change: "Change",
        accuracy: "Accuracy",
        
        // Prediction results
        rise: "Rise",
        fall: "Fall",
        
        // Statistics
        prediction_stats: "Prediction Statistics",
        
        // Confirmations and hints
        confirm_reset: "Are you sure you want to reset prediction history?",
        history_reset: "Prediction history has been reset",
        reset_failed: "Reset failed",
        please_select_date: "Please select a date",
        
        // data_input.html related
        manual_data_title: "Manual Historical Data Input",
        select_date: "Select Date: ",
        load_date_data: "Load Data for This Date",
        back_to_home: "Back to Home",
        forex_data: "Forex Data",
        bond_data: "Bond Yield Data (%)",
        news_data: "News Data",
        china_news_count: "China News Count",
        china_news_tone: "China News Sentiment",
        us_news_count: "US News Count",
        us_news_tone: "US News Sentiment",
        uk_news_count: "UK News Count",
        uk_news_tone: "UK News Sentiment",
        save_data: "Save Data",
        view_existing: "View Existing Data Dates",
        existing_dates: "Existing Data Dates",
        data_save_success: "Data saved successfully!",
        save_failed: "Save failed",
        data_load_success: "Data loaded successfully",
        no_data_for_date: "No data for this date",
        load_failed: "Load failed",
        total_days: "Total",
        days_of_data: "days of data",
        data_completeness: "Data Completeness",
        complete: "Complete",
        incomplete: "Incomplete",
        no_data_yet: "No data yet",
        get_dates_failed: "Failed to get date list",
        china_bond: "China Bond",
        us_bond: "US Bond",
        uk_bond: "UK Bond",
        
        // Trading related
        trading_settings: "Trading Settings",
        initial_balance: "Initial Balance",
        current_balance: "Current Balance",
        allocation_settings: "Fund Allocation Settings (%)",
        auto_trade: "Auto Trade",
        auto_trade_time: "Auto Trade Time",
        save_settings: "Save Settings",
        performance_stats: "Performance Stats",
        recent_trades: "Recent Trades",
        total_profit: "Total Profit/Loss",
        win_rate: "Win Rate",
        total_trades: "Total Trades",
        winning_trades: "Winning Trades",
        allocation_must_be_100: "Allocation must sum to 100%! Current sum: {total}%",
        settings_saved: "Settings saved",
        save_settings_failed: "Failed to save settings",
        base_currency: "Base Currency",
        currency_holdings: "Currency Holdings",
        allocation_hint: "Trade amount automatically adjusted based on model accuracy. Pairs with accuracy below 50% will not be traded",
        portfolio_value: "Portfolio Value",
        reset_portfolio: "Reset Portfolio",
        confirm_reset_portfolio: "Are you sure you want to reset the portfolio? All currencies will be reset to initial state",
        portfolio_reset: "Portfolio has been reset",
        reset_portfolio_failed: "Failed to reset portfolio",

        normal: "Normal",
        reverse: "Reverse",
        current_normal: "Current: Normal Trading",
        current_reverse: "Current: Reverse Trading", 
        initial_stage: "Initial Stage: Conservative Trading Mode",
        auto_reverse_hint: "Accuracy below 50%, will auto-reverse trades",
        no_trades_yet: "No trades yet",
        load_history_failed: "Failed to load trade history",
    }
};

// 获取当前语言
function getCurrentLanguage() {
    return localStorage.getItem('language') || 'zh';
}

// 设置语言
function setLanguage(lang) {
    localStorage.setItem('language', lang);
    applyTranslations();
    updateLanguageButtons();
    
    // 如果是在主页面，刷新数据显示
    if (typeof checkSystemStatus !== 'undefined') {
        checkSystemStatus();
        showLatestData();
    }
}

// 应用翻译
function applyTranslations() {
    const lang = getCurrentLanguage();
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // 更新页面语言属性
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
}

// 更新语言按钮状态
function updateLanguageButtons() {
    const lang = getCurrentLanguage();
    const zhBtn = document.getElementById('zh-btn');
    const enBtn = document.getElementById('en-btn');
    
    if (zhBtn && enBtn) {
        if (lang === 'zh') {
            zhBtn.classList.add('active');
            enBtn.classList.remove('active');
        } else {
            zhBtn.classList.remove('active');
            enBtn.classList.add('active');
        }
    }
}

// 获取翻译文本
function t(key) {
    const lang = getCurrentLanguage();
    return translations[lang][key] || key;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    applyTranslations();
    updateLanguageButtons();
});