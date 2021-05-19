from . import processor

class _Youtube(processor.Processor):
    """Process AMP youtube test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        points.append({
            "measurement": "video",
            "tags": {
                "test": "youtube",
                "source": source,
                "destination": data["video"],
                "requested_quality": data["requested_quality"],
            },
            "time": timestamp,
            "fields": {
                "actual_quality": data["actual_quality"],
                "pre_time": data["pre_time"],
                "initial_buffering": data["initial_buffering"],
                "playing_time": data["playing_time"],
                "stall_time": data["stall_time"],
                "stall_count": data["stall_count"],
                "count": 1 if self._is_valid(data["playing_time"]) else 0,
            }
        })
        return points

process = _Youtube().process
