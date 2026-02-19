"""AI Engine for Smart-Encrypt"""
import re
import hashlib
import time
import random
from typing import List, Dict
import threading

class AIEngine:
    def __init__(self):
        self.threat_patterns = [
            r'(?i)(malware|virus|trojan|ransomware)',
            r'(?i)(phishing|scam|fraud)',
            r'(?i)(exploit|vulnerability|0day)',
            r'(?i)(botnet|ddos|attack)',
            r'(?i)(keylogger|spyware|backdoor)'
        ]
        
        self.phishing_indicators = [
            'urgent action required',
            'verify your account',
            'suspended account',
            'click here immediately',
            'limited time offer'
        ]
        
        self.malware_signatures = {
            'trojan': ['CreateRemoteThread', 'WriteProcessMemory', 'VirtualAllocEx'],
            'ransomware': ['CryptEncrypt', 'FindFirstFile', 'MoveFile'],
            'keylogger': ['GetAsyncKeyState', 'SetWindowsHookEx', 'CallNextHookEx']
        }
    
    def analyze_threat_intelligence(self, text: str) -> Dict:
        """Analyze text for threat intelligence"""
        threats = []
        confidence = 0
        
        for pattern in self.threat_patterns:
            matches = re.findall(pattern, text)
            if matches:
                threats.extend(matches)
                confidence += len(matches) * 20
        
        # Analyze suspicious patterns
        suspicious_patterns = [
            r'(?i)\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
            r'(?i)[a-z0-9]{32,}',  # Long hex strings (hashes)
            r'(?i)(base64|encoded|encrypted)',
            r'(?i)(payload|shellcode|exploit)'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text):
                confidence += 10
        
        return {
            'threats_detected': list(set(threats)),
            'confidence_score': min(confidence, 100),
            'risk_level': self._calculate_risk_level(confidence),
            'recommendations': self._generate_recommendations(threats)
        }
    
    def classify_malware(self, file_content: str) -> Dict:
        """Classify potential malware based on content"""
        classifications = []
        confidence_scores = {}
        
        for malware_type, signatures in self.malware_signatures.items():
            matches = 0
            for signature in signatures:
                if signature.lower() in file_content.lower():
                    matches += 1
            
            if matches > 0:
                classifications.append(malware_type)
                confidence_scores[malware_type] = (matches / len(signatures)) * 100
        
        return {
            'classifications': classifications,
            'confidence_scores': confidence_scores,
            'total_signatures': sum(len(sigs) for sigs in self.malware_signatures.values()),
            'matches_found': sum(confidence_scores.values()) / 100 if confidence_scores else 0
        }
    
    def detect_phishing(self, text: str) -> Dict:
        """Detect phishing attempts in text"""
        indicators_found = []
        
        for indicator in self.phishing_indicators:
            if indicator.lower() in text.lower():
                indicators_found.append(indicator)
        
        # Check for suspicious URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        suspicious_urls = []
        for url in urls:
            if any(suspicious in url.lower() for suspicious in ['bit.ly', 'tinyurl', 'short']):
                suspicious_urls.append(url)
        
        risk_score = len(indicators_found) * 20 + len(suspicious_urls) * 15
        
        return {
            'is_phishing': risk_score > 30,
            'risk_score': min(risk_score, 100),
            'indicators_found': indicators_found,
            'suspicious_urls': suspicious_urls,
            'recommendation': 'HIGH RISK - Do not click links' if risk_score > 50 else 'MEDIUM RISK - Verify sender'
        }
    
    def anomaly_detection(self, data_points: List[float]) -> Dict:
        """Detect anomalies in data patterns"""
        if len(data_points) < 3:
            return {'anomalies': [], 'threshold': 0}
        
        mean = sum(data_points) / len(data_points)
        variance = sum((x - mean) ** 2 for x in data_points) / len(data_points)
        std_dev = variance ** 0.5
        
        threshold = mean + (2 * std_dev)  # 2 standard deviations
        anomalies = [i for i, x in enumerate(data_points) if x > threshold]
        
        return {
            'anomalies': anomalies,
            'threshold': threshold,
            'mean': mean,
            'std_deviation': std_dev,
            'anomaly_count': len(anomalies)
        }
    
    def pattern_recognition(self, text: str) -> Dict:
        """Recognize patterns in text data"""
        patterns = {
            'email_addresses': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'ip_addresses': re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text),
            'phone_numbers': re.findall(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b', text),
            'credit_cards': re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text),
            'social_security': re.findall(r'\b\d{3}-\d{2}-\d{4}\b', text),
            'urls': re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            'bitcoin_addresses': re.findall(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', text),
            'file_hashes': re.findall(r'\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b', text)
        }
        
        # Calculate sensitivity score
        sensitive_count = sum(len(patterns[key]) for key in ['credit_cards', 'social_security', 'bitcoin_addresses'])
        sensitivity_score = min(sensitive_count * 25, 100)
        
        return {
            'patterns': patterns,
            'sensitivity_score': sensitivity_score,
            'total_patterns': sum(len(v) for v in patterns.values()),
            'high_risk_patterns': sensitive_count
        }
    
    def auto_exploitation_analysis(self, target_info: Dict) -> Dict:
        """Analyze target for potential exploitation vectors"""
        vectors = []
        
        # Mock analysis based on target info
        if 'ports' in target_info:
            for port in target_info['ports']:
                if port in [21, 22, 23, 80, 443, 3389]:
                    vectors.append({
                        'port': port,
                        'service': self._get_service_name(port),
                        'vulnerability': self._get_mock_vulnerability(port),
                        'severity': random.choice(['low', 'medium', 'high', 'critical'])
                    })
        
        return {
            'target': target_info.get('ip', 'unknown'),
            'exploitation_vectors': vectors,
            'total_vectors': len(vectors),
            'recommended_tools': ['nmap', 'metasploit', 'burpsuite'],
            'success_probability': random.randint(20, 80)
        }
    
    def _calculate_risk_level(self, confidence: int) -> str:
        """Calculate risk level based on confidence score"""
        if confidence >= 80:
            return 'CRITICAL'
        elif confidence >= 60:
            return 'HIGH'
        elif confidence >= 40:
            return 'MEDIUM'
        elif confidence >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _generate_recommendations(self, threats: List[str]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if any('malware' in threat.lower() for threat in threats):
            recommendations.append('Run full system antivirus scan')
            recommendations.append('Update all software and OS')
        
        if any('phishing' in threat.lower() for threat in threats):
            recommendations.append('Verify sender identity')
            recommendations.append('Do not click suspicious links')
        
        if any('exploit' in threat.lower() for threat in threats):
            recommendations.append('Apply security patches immediately')
            recommendations.append('Enable firewall protection')
        
        return recommendations or ['Monitor for suspicious activity']
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port"""
        services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            80: 'HTTP',
            443: 'HTTPS',
            3389: 'RDP'
        }
        return services.get(port, 'Unknown')
    
    def _get_mock_vulnerability(self, port: int) -> str:
        """Get mock vulnerability for port"""
        vulns = {
            21: 'Anonymous FTP access',
            22: 'Weak SSH configuration',
            23: 'Unencrypted Telnet',
            80: 'Directory traversal',
            443: 'SSL/TLS misconfiguration',
            3389: 'RDP brute force'
        }
        return vulns.get(port, 'Unknown vulnerability')