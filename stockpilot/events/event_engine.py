class EventEngine:
    def analyze(self, event):
        return {
            'event': event,
            'impact': 'unknown',
            'related_companies': []
        }

    def map_event_to_theme(self, event):
        keywords = {
            'AI': 'AI算力',
            '存储': 'AI存储',
            '半导体': '国产替代'
        }
        result = []
        for key, value in keywords.items():
            if key in event:
                result.append(value)
        return result
