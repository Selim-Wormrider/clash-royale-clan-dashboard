echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "📄 Creating .env file..."
cp .env.example .env

echo "🧩 Writing systemd service..."
cat > /etc/systemd/system/clash-dashboard.service <<EOF
[Unit]
Description=Clash Royale Clan Dashboard
After=network.target

[Service]
User=root
WorkingDirectory=/opt/dashboard
EnvironmentFile=/opt/dashboard/.env
ExecStart=/opt/dashboard/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Enabling and starting dashboard service..."
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable clash-dashboard
systemctl restart clash-dashboard

echo "🧰 Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/clash-dashboard <<EOF
server {
    listen 80;
    server_name dashboard.mycoenvy.store;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_redirect     off;
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/clash-dashboard /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# echo "🔐 Setting up SSL with Let's Encrypt..."
# certbot --nginx --non-interactive --agree-tos --redirect -m you@example.com -d dashboard.mycoenvy.store

echo "✅ Setup complete. Visit: https://dashboard.mycoenvy.store"
