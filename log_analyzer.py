import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LogAnalyzer:
    def __init__(self, file_path: str):
        
        self.file_path = file_path
        self.log_pattern = r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}).*?\[(?P<date>.*?)\]\s"(?P<method>[A-Z]+)\s.*?HTTP/\d\.\d"\s(?P<status>\d{3})'
        self.parsed_data: List[Dict[str, str]] = []
        
    def parse(self) -> List[Dict[str, str]]:
        
        try:
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    match = re.search(self.log_pattern, line)
                    
                    if match:
                        self.parsed_data.append(match.groupdict())
                    else:
                        logger.warning(f"Error in line {line_num}: {line[:30]}")
                        
            return self.parsed_data
        
        except Exception as e:

            logger.error(f"Critical error: {e}")
            return []
        
    def count_by_status(self, status_code: str) -> int:

        count = sum(1 for entry in self.parsed_data if entry["status"] == status_code)
        logger.info(f"Status {status_code}: {count}")
        return count
    
if __name__ == "__main__":
    analyzer = LogAnalyzer("server.log")
    if analyzer.parse():
        analyzer.count_by_status("200")
