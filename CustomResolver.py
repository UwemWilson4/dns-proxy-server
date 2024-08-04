from dnslib import DNSRecord, RCODE, QTYPE, RR, A
from dnslib.server import DNSServer, BaseResolver
from ModelTrainer import extract_features
import socket
import logging
import json
import joblib
import pandas as pd

# Set the logging level to INFO
logging.basicConfig(filename='dns_proxy_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomResolver(BaseResolver):

    def __init__(self):
        # Load the trained model
        self.model = joblib.load('random_forest_model.pkl')

    def resolve(self, request, handler):
        logger.info(f"Received request: {request}. Processing...")
        # Extract the requested domain and query type
        qname = request.q.qname
        qtype = request.q.qtype
        domain = str(qname)

        # Check if the requested domain is safe by querying the ML model
        is_malicious = self.query_ml_model(domain)

        if is_malicious:
            print(f"Domain {domain} is malicious")
            logger.info(f"Domain {domain} is malicious")
            # If the domain is blocked, return a custom response
            reply = request.reply()
            reply.header.rcode = RCODE.REFUSED
            reply.add_answer = reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            return reply
        else:
            print(f"Domain {domain} is safe")
            logger.info(f"Domain {domain} is safe")
            # Otherwise, forward the request to an upstream DNS server
            return self.forward_to_google_dns(request)  

    def query_ml_model(self, domain):
        print(f"Querying ML model for {domain}")

        # Extract features from the domain
        features = [extract_features(domain)]
        features_df = pd.DataFrame(features, columns=['length', 'dot_count', 'has_http', 'has_www', 'has_at', 'ends_with_html', 'contains_youtube'])
        prediction = self.model.predict(features_df)

        # Example response: {'is_malicious': False, 'confidence': 0.9999999999999999}
        if prediction[0] == 1:
            logger.info(f"Domain {domain} is predicted to be malicious")
        else:
            logger.info(f"Domain {domain} is predicted to be safe")

        return prediction[0]
    
    def forward_to_google_dns(self, request):
        # Forward the request to Google's public DNS server (8.8.8.8)
        logger.info("Forwarding request to Google's public DNS server")
        upstream_server = '8.8.8.8'
        upstream_port = 53

        # Convert the request to bytes
        request_bytes = request.pack()

        # Send the request to Google's public DNS server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(request_bytes, (upstream_server, upstream_port))
            response_bytes, _ = sock.recvfrom(512)
            logger.info(f"Received response from Google's public DNS server: {response_bytes}")

        # Parse the response
        reply = DNSRecord.parse(response_bytes)
        return reply
    
if __name__ == '__main__':
    resolver = CustomResolver()
    print("Resolver created")
    logger.info("Resolver created")
    print("Starting DNS server")
    logger.info("Starting DNS server")
    server = DNSServer(resolver, port=5353, address='127.0.0.1')
    server.start()