#!/bin/bash
lsof -ti:8502 | xargs kill -9 2>/dev/null
nohup /opt/anaconda3/bin/python -m streamlit run ~/Projects/health-portfolio-lab-trends/app.py \
  --server.headless true \
  > /tmp/lab_trends.log 2>&1 &
sleep 3
open http://localhost:8502
