*/30 * * * * make run >> /var/log/cron.log 2>&1 && \
0 9 * * * make report >> /var/log/cron.log 2>&1
