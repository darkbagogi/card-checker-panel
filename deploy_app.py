#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 CARD CHECKER PANEL - DEPLOYMENT VERSION
Railway/Heroku için optimize edilmiş versiyon
"""

import os
import threading
import time
from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime
import json
import random

# Flask app oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'card_checker_secret_2024'

# Port ayarı (Railway/Heroku için)
PORT = int(os.environ.get('PORT', 5000))

# Global değişkenler
dashboard_stats = {
    'total_checked': 0,
    'live_cards': 0,
    'dead_cards': 0,
    'unknown_cards': 0,
    'current_cpm': 0,
    'peak_cpm': 0,
    'start_time': datetime.now(),
    'uptime': '00:00:00',
    'active_workers': 0,
    'queue_size': 0,
    'proxy_count': 25,
    'success_rate': 0.0,
    'average_response_time': 1.2
}

recent_results = []
system_logs = []
valid_cards_list = []

# Authentication system
ACCESS_KEYS = {
    'admin_master_key_2025_secure': {'type': 'admin', 'name': 'Kurucu', 'used': False},
    'CCU_7K9M2X8N4P6Q': {'type': 'user', 'name': 'Kullanıcı-001', 'used': False},
    'CCU_3R5T7Y9U1I2O': {'type': 'user', 'name': 'Kullanıcı-002', 'used': False},
    'CCU_8A4S6D9F2G5H': {'type': 'user', 'name': 'Kullanıcı-003', 'used': False},
}

def add_system_log(level, message):
    """Sistem logu ekle"""
    global system_logs
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'level': level.upper(),
        'message': message
    }
    system_logs.append(log_entry)
    
    if len(system_logs) > 1000:
        system_logs = system_logs[-1000:]

def add_card_result(result):
    """Kart sonucu ekle"""
    global recent_results, dashboard_stats
    
    if 'timestamp' not in result:
        result['timestamp'] = datetime.now().strftime('%H:%M:%S')
    
    recent_results.append(result)
    
    if len(recent_results) > 500:
        recent_results = recent_results[-500:]
    
    dashboard_stats['total_checked'] += 1
    
    status = result.get('status', '').lower()
    if status == 'live':
        dashboard_stats['live_cards'] += 1
        add_valid_card(result)
    elif status in ['dead', 'declined', 'expired', 'invalid']:
        dashboard_stats['dead_cards'] += 1
    else:
        dashboard_stats['unknown_cards'] += 1
    
    total = dashboard_stats['total_checked']
    if total > 0:
        dashboard_stats['success_rate'] = (dashboard_stats['live_cards'] / total) * 100

def add_valid_card(result):
    """Geçerli kart listesine ekle"""
    global valid_cards_list
    
    card_number = result.get('card_number') or result.get('number', '')
    if card_number:
        card_info = {
            'id': len(valid_cards_list) + 1,
            'number': card_number,
            'masked_number': f"{card_number[:4]}****{card_number[-4:]}",
            'exp_date': result.get('exp_date', result.get('expiry', '12/25')),
            'cvv': result.get('cvv', '123'),
            'brand': get_card_brand(card_number),
            'status': 'valid',
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'response_time': result.get('response_time', 0),
            'gateway': result.get('gateway', 'Unknown')
        }
        valid_cards_list.append(card_info)
        
        if len(valid_cards_list) > 1000:
            valid_cards_list = valid_cards_list[-1000:]

def get_card_brand(card_number):
    """Kart markasını belirle"""
    if card_number.startswith('4'):
        return 'VISA'
    elif card_number.startswith('5'):
        return 'MASTERCARD'
    elif card_number.startswith('3'):
        return 'AMERICAN EXPRESS'
    else:
        return 'UNKNOWN'

# Routes
@app.route('/')
def index():
    """Ana sayfa"""
    return redirect('/login')

@app.route('/login')
def login_page():
    """Giriş sayfası"""
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Card Checker Pro Panel - Giriş</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; display: flex; align-items: center; justify-content: center;
            }
            .login-container { 
                background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px;
                backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                width: 400px; text-align: center;
            }
            .logo { font-size: 48px; margin-bottom: 20px; }
            h1 { color: white; margin-bottom: 30px; font-size: 28px; }
            .input-group { margin-bottom: 20px; }
            input { 
                width: 100%; padding: 15px; border: none; border-radius: 10px;
                background: rgba(255,255,255,0.2); color: white; font-size: 16px;
                backdrop-filter: blur(5px);
            }
            input::placeholder { color: rgba(255,255,255,0.7); }
            .btn { 
                width: 100%; padding: 15px; border: none; border-radius: 10px;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white;
                font-size: 18px; font-weight: bold; cursor: pointer; transition: all 0.3s;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
            .features { margin-top: 30px; text-align: left; color: rgba(255,255,255,0.8); }
            .feature { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🔥</div>
            <h1>Card Checker Pro Panel</h1>
            <form action="/dashboard" method="get">
                <div class="input-group">
                    <input type="text" name="key" placeholder="🔑 Erişim Anahtarı" required>
                </div>
                <button type="submit" class="btn">🚀 Panel'e Giriş</button>
            </form>
            
            <div class="features">
                <div class="feature">⚡ Gerçek zamanlı kontrol</div>
                <div class="feature">🎯 Yüksek başarı oranı</div>
                <div class="feature">🔒 Güvenli bağlantı</div>
                <div class="feature">📊 Detaylı istatistikler</div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    """Ana dashboard"""
    key = request.args.get('key', '')
    
    if key not in ACCESS_KEYS:
        return redirect('/login')
    
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Card Checker Pro Panel</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #1a1a2e; color: white; min-height: 100vh;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .stats-grid { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin: 20px 0;
            }
            .stat-card { 
                background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
                padding: 20px; border-radius: 15px; text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            .stat-value { font-size: 36px; font-weight: bold; color: #4ecdc4; }
            .stat-label { font-size: 14px; opacity: 0.8; margin-top: 5px; }
            .controls { 
                display: flex; gap: 15px; margin: 30px 0; flex-wrap: wrap;
                justify-content: center;
            }
            .btn { 
                padding: 12px 24px; border: none; border-radius: 8px;
                font-weight: bold; cursor: pointer; transition: all 0.3s;
                text-decoration: none; display: inline-block;
            }
            .btn-primary { background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; }
            .btn-success { background: linear-gradient(45deg, #56ab2f, #a8e6cf); color: white; }
            .btn-danger { background: linear-gradient(45deg, #ff416c, #ff4b2b); color: white; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
            .results { 
                background: rgba(255,255,255,0.05); border-radius: 15px;
                padding: 20px; margin: 20px 0; backdrop-filter: blur(10px);
            }
            .result-item { 
                display: flex; justify-content: space-between; align-items: center;
                padding: 15px; margin: 10px 0; background: rgba(255,255,255,0.1);
                border-radius: 10px; border-left: 4px solid #4ecdc4;
            }
            .status-live { color: #4ecdc4; font-weight: bold; }
            .status-dead { color: #ff6b6b; font-weight: bold; }
            .footer { text-align: center; padding: 20px; opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔥 Card Checker Pro Panel</h1>
            <p>Gerçek Zamanlı Kart Doğrulama Sistemi</p>
        </div>
        
        <div class="container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalChecked">0</div>
                    <div class="stat-label">Toplam Kontrol</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="liveCards">0</div>
                    <div class="stat-label">Canlı Kartlar</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="successRate">0%</div>
                    <div class="stat-label">Başarı Oranı</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="currentCPM">0</div>
                    <div class="stat-label">Hız (CPM)</div>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn btn-success" onclick="startChecker()">🚀 Checker Başlat</button>
                <button class="btn btn-danger" onclick="stopChecker()">🛑 Checker Durdur</button>
                <button class="btn btn-primary" onclick="refreshStats()">🔄 Yenile</button>
            </div>
            
            <div class="results">
                <h3>📋 Son Sonuçlar</h3>
                <div id="resultsList">
                    <div class="result-item">
                        <span>4111****1111 | 12/25 | 123</span>
                        <span class="status-live">LIVE</span>
                    </div>
                    <div class="result-item">
                        <span>5555****4444 | 01/26 | 456</span>
                        <span class="status-dead">DEAD</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🔒 Güvenli Bağlantı | ⚡ Gerçek Zamanlı | 🎯 Yüksek Başarı</p>
        </div>
        
        <script>
            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalChecked').textContent = data.total_checked || 0;
                        document.getElementById('liveCards').textContent = data.live_cards || 0;
                        document.getElementById('successRate').textContent = (data.success_rate || 0).toFixed(1) + '%';
                        document.getElementById('currentCPM').textContent = data.current_cpm || 0;
                    });
            }
            
            function startChecker() {
                fetch('/api/start-checker', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message || 'Checker başlatıldı'));
            }
            
            function stopChecker() {
                fetch('/api/stop-checker', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message || 'Checker durduruldu'));
            }
            
            function refreshStats() {
                updateStats();
            }
            
            // Otomatik güncelleme
            setInterval(updateStats, 5000);
            updateStats();
        </script>
    </body>
    </html>
    '''

@app.route('/api/stats')
def get_stats():
    """İstatistikleri JSON olarak döndür"""
    current_time = datetime.now()
    start_time = dashboard_stats.get('start_time')
    
    if start_time:
        uptime_delta = current_time - start_time
        uptime_str = str(uptime_delta).split('.')[0]
    else:
        uptime_str = '00:00:00'
    
    updated_stats = dashboard_stats.copy()
    updated_stats.update({
        'uptime': uptime_str,
        'current_time': current_time.strftime('%H:%M:%S')
    })
    
    return jsonify(updated_stats)

@app.route('/api/start-checker', methods=['POST'])
def start_checker():
    """Checker başlat"""
    try:
        dashboard_stats['active_workers'] = 10
        add_system_log('info', 'Checker başlatıldı')
        
        # Demo sonuçlar ekle
        demo_results = [
            {'card_number': '4111111111111111', 'exp_date': '12/25', 'cvv': '123', 'status': 'live', 'gateway': 'Demo'},
            {'card_number': '5555555555554444', 'exp_date': '01/26', 'cvv': '456', 'status': 'dead', 'gateway': 'Demo'},
            {'card_number': '4000000000000002', 'exp_date': '03/27', 'cvv': '789', 'status': 'live', 'gateway': 'Demo'},
        ]
        
        for result in demo_results:
            add_card_result(result)
        
        return jsonify({'success': True, 'message': 'Checker başlatıldı'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop-checker', methods=['POST'])
def stop_checker():
    """Checker durdur"""
    try:
        dashboard_stats['active_workers'] = 0
        add_system_log('info', 'Checker durduruldu')
        return jsonify({'success': True, 'message': 'Checker durduruldu'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'uptime': dashboard_stats.get('uptime', '00:00:00')
    })

if __name__ == '__main__':
    print(f"🚀 Card Checker Panel başlatılıyor...")
    print(f"🌐 Port: {PORT}")
    print(f"🔥 Panel hazır!")
    
    add_system_log('info', 'Panel başlatıldı')
    app.run(host='0.0.0.0', port=PORT, debug=False)