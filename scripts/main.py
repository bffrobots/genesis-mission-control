#!/usr/bin/env python3
"""
Genesis Mission Control - Servo Backend
Controls 18 DOF Mini BFF Genesis via Synthiam ARC HTTP Server

Runs on Windows to communicate with ARC via file-based interface.
"""

import os
import sys
import json
import time
import socket
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ═══════════════════════════════════════════════════════════
# CONFIGURATION - Auto-detects Windows username
# ═══════════════════════════════════════════════════════════

# Get Windows username from environment variable
WINDOWS_USERNAME = os.environ.get('USERNAME', 'Perseus')

# Auto-detect HTTP Server Root directory
if sys.platform == 'win32':
    # Running natively on Windows
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    VARIABLES_DIR = os.path.join(
        os.environ.get('USERPROFILE', f'C:\\Users\\{WINDOWS_USERNAME}'),
        'Documents', 'ARC', 'HTTP Server Root'
    )
else:
    # Running on WSL - access Windows filesystem via /mnt/c
    VARIABLES_DIR = f'/mnt/c/Users/{WINDOWS_USERNAME}/Documents/ARC/HTTP Server Root'

# Verify directory exists
if not os.path.exists(VARIABLES_DIR):
    print(f"⚠️  Warning: VARIABLES_DIR not found: {VARIABLES_DIR}")
    print(f"   Please ensure ARC HTTP Server Root is set to this directory")
    print(f"   Or create the directory manually")

print(f"📁 Variables Directory: {VARIABLES_DIR}")

# ═══════════════════════════════════════════════════════════
# FLASK APP
# ═══════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Servo state cache
servo_positions = {}

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.route('/api/servo', methods=['POST'])
def move_servo():
    """
    Move servo to position via ARC HTTP Server
    
    JSON body:
    {
        "servo_id": 0,      # Servo ID (0-17)
        "position": 90,     # Position (0-180 degrees)
        "port": "D0"        # Optional: ARC port name
    }
    """
    try:
        data = request.json
        servo_id = data.get('servo_id')
        position = data.get('position')
        port = data.get('port', f'D{servo_id}')
        
        # Validate position
        if not isinstance(position, int) or position < 0 or position > 180:
            return jsonify({
                'error': 'Position must be integer between 0-180',
                'success': False
            }), 400
        
        # Write to ARC HTTP Server Root
        filename = f'Servo_{port}.txt'
        filepath = os.path.join(VARIABLES_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(str(position))
        
        # Update cache
        servo_positions[servo_id] = position
        
        print(f'✅ Servo {port} -> {position}°')
        
        return jsonify({
            'success': True,
            'servo_id': servo_id,
            'position': position,
            'port': port,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f'❌ Error moving servo: {e}')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/servo/all', methods=['POST'])
def move_all_servos():
    """
    Move all servos to positions
    
    JSON body:
    {
        "servos": {
            "D0": 90,
            "D1": 45,
            ...
        }
    }
    """
    try:
        data = request.json
        servos = data.get('servos', {})
        
        for port, position in servos.items():
            if 0 <= position <= 180:
                filename = f'Servo_{port}.txt'
                filepath = os.path.join(VARIABLES_DIR, filename)
                
                with open(filepath, 'w') as f:
                    f.write(str(position))
                
                servo_id = int(port[1:]) if port[1:].isdigit() else port
                servo_positions[servo_id] = position
        
        print(f'✅ Moved {len(servos)} servos')
        
        return jsonify({
            'success': True,
            'moved': len(servos)
        })
        
    except Exception as e:
        print(f'❌ Error moving servos: {e}')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/estop', methods=['POST'])
def emergency_stop():
    """
    Emergency stop - disable all servos
    """
    try:
        # Write E-STOP flag
        estop_file = os.path.join(VARIABLES_DIR, 'Genesis_EStop.txt')
        with open(estop_file, 'w') as f:
            f.write('1')
        
        print('🛑 E-STOP ACTIVATED')
        
        return jsonify({
            'success': True,
            'message': 'E-STOP ACTIVATED'
        })
        
    except Exception as e:
        print(f'❌ E-STOP error: {e}')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/pose', methods=['POST'])
def set_pose():
    """
    Load and execute a pose
    
    JSON body:
    {
        "pose_name": "stand",
        "servos": {"D0": 90, "D1": 45, ...}
    }
    """
    try:
        data = request.json
        pose_name = data.get('pose_name', 'custom')
        servos = data.get('servos', {})
        
        print(f'🎯 Loading pose: {pose_name}')
        
        # Move all servos
        for port, position in servos.items():
            if 0 <= position <= 180:
                filename = f'Servo_{port}.txt'
                filepath = os.path.join(VARIABLES_DIR, filename)
                
                with open(filepath, 'w') as f:
                    f.write(str(position))
                
                time.sleep(0.05)  # Small delay between servos
        
        print(f'✅ Pose {pose_name} complete')
        
        return jsonify({
            'success': True,
            'pose': pose_name
        })
        
    except Exception as e:
        print(f'❌ Pose error: {e}')
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'robot': 'mini-bff-genesis',
        'robot_name': 'Genesis',
        'servos': len(servo_positions),
        'variables_dir': VARIABLES_DIR,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/servos', methods=['GET'])
def get_servo_positions():
    """Get current servo positions"""
    return jsonify({
        'servos': servo_positions,
        'count': len(servo_positions)
    })

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('=' * 60)
    print('Genesis Mission Control - Servo Backend')
    print('Mini BFF Genesis (18 DOF)')
    print('=' * 60)
    print(f'Windows Username: {WINDOWS_USERNAME}')
    print(f'Variables Directory: {VARIABLES_DIR}')
    print(f'Platform: {sys.platform}')
    print()
    print('Starting HTTP server...')
    print('Listening on http://localhost:5000')
    print()
    print('Endpoints:')
    print('  POST /api/servo      - Move single servo')
    print('  POST /api/servo/all  - Move all servos')
    print('  POST /api/pose       - Execute pose')
    print('  POST /api/estop      - Emergency stop')
    print('  GET  /status         - Health check')
    print('  GET  /api/servos     - Get servo positions')
    print()
    print('Press Ctrl+C to stop')
    print('=' * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
