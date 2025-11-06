FROM python:3.12-slim

WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY salesforce-mcp-server/ ./salesforce-mcp-server/
# COPY salesforce_agent/ ./salesforce_agent/
# COPY host_agent_salesforce/ ./host_agent_salesforce/
# COPY agent/ ./agent/
# COPY .env .

# # Install agent dependencies
RUN cd salesforce_agent && pip install -e . --no-deps
RUN cd host_agent_salesforce && pip install -e . --no-deps

# RUN pip install -e ./salesforce_agent
# RUN pip install -e ./host_agent_salesforce

EXPOSE 8002 10003 10004

CMD ["python", "salesforce-mcp-server/mcp_servers/salesforce_agent_server.py"]