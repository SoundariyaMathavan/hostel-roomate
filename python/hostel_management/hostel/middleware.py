from django.utils.deprecation import MiddlewareMixin
from django.utils.safestring import mark_safe

class ChatbotScriptMiddleware(MiddlewareMixin):
    """
    Middleware to inject the chatbot scripts into all HTML responses.
    """
    def process_response(self, request, response):
        if response.get('Content-Type', '').startswith('text/html'):
            # Only inject into HTML responses
            content = response.content.decode('utf-8')
            
            # Scripts to inject
            scripts = [
                '<script src="/static/js/chatbot.js"></script>',
                '<script src="/static/js/back-to-top.js"></script>'
            ]
            
            # Insert scripts before closing body tag
            if '</body>' in content:
                script_tags = '\n'.join(scripts)
                content = content.replace('</body>', f'{script_tags}\n</body>')
            else:
                # If no body tag, append to the end
                content += '\n' + '\n'.join(scripts)
            
            # Update the response content
            response.content = content.encode('utf-8')
            
            # Update Content-Length header if it exists
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        
        return response