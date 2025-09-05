# 企业微信配置类
import os
from typing import Optional

class WeChatConfig:
    """企业微信配置"""
    
    def __init__(self):
        self.corp_id = os.getenv('WECHAT_CORP_ID')
        self.corp_secret = os.getenv('WECHAT_CORP_SECRET')
        self.agent_id = os.getenv('WECHAT_AGENT_ID')
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[int] = None
    
    def get_access_token(self) -> str:
        """获取企业微信访问令牌"""
        import requests
        import time
        
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('errcode') == 0:
            self.access_token = data['access_token']
            self.token_expires_at = time.time() + data['expires_in'] - 60  # 提前1分钟过期
            return self.access_token
        else:
            raise Exception(f"获取企业微信访问令牌失败: {data}")
