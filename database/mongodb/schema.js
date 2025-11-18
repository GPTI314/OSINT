// ============================================================================
// OSINT Platform - MongoDB Collections Schema
// ============================================================================
// Version: 1.0.0
// Description: MongoDB collections for unstructured data and logging
// ============================================================================

// Use OSINT database
use osint_platform;

// ============================================================================
// SCRAPING LOGS COLLECTION
// ============================================================================
// Detailed logs for all scraping operations

db.createCollection("scraping_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["job_id", "timestamp", "level", "message"],
            properties: {
                job_id: {
                    bsonType: "string",
                    description: "UUID of the scraping job"
                },
                investigation_id: {
                    bsonType: "string",
                    description: "UUID of the investigation"
                },
                timestamp: {
                    bsonType: "date",
                    description: "Log timestamp"
                },
                level: {
                    enum: ["debug", "info", "warning", "error", "critical"],
                    description: "Log level"
                },
                message: {
                    bsonType: "string",
                    description: "Log message"
                },
                url: {
                    bsonType: "string",
                    description: "URL being scraped"
                },
                status_code: {
                    bsonType: "int",
                    description: "HTTP status code"
                },
                response_time: {
                    bsonType: "double",
                    description: "Response time in milliseconds"
                },
                error: {
                    bsonType: "object",
                    description: "Error details if any"
                },
                context: {
                    bsonType: "object",
                    description: "Additional context data"
                },
                user_agent: {
                    bsonType: "string",
                    description: "User agent used"
                },
                proxy: {
                    bsonType: "string",
                    description: "Proxy used if any"
                }
            }
        }
    }
});

// Indexes for scraping_logs
db.scraping_logs.createIndex({ "job_id": 1, "timestamp": -1 });
db.scraping_logs.createIndex({ "investigation_id": 1, "timestamp": -1 });
db.scraping_logs.createIndex({ "level": 1, "timestamp": -1 });
db.scraping_logs.createIndex({ "timestamp": -1 });
db.scraping_logs.createIndex({ "url": 1 });

// TTL index to automatically delete logs older than 90 days
db.scraping_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 7776000 });

// ============================================================================
// CRAWLING LOGS COLLECTION
// ============================================================================
// Detailed logs for crawling sessions

db.createCollection("crawling_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["session_id", "timestamp", "level", "message"],
            properties: {
                session_id: {
                    bsonType: "string",
                    description: "UUID of the crawling session"
                },
                investigation_id: {
                    bsonType: "string",
                    description: "UUID of the investigation"
                },
                timestamp: {
                    bsonType: "date",
                    description: "Log timestamp"
                },
                level: {
                    enum: ["debug", "info", "warning", "error", "critical"],
                    description: "Log level"
                },
                message: {
                    bsonType: "string",
                    description: "Log message"
                },
                url: {
                    bsonType: "string",
                    description: "URL being crawled"
                },
                depth: {
                    bsonType: "int",
                    description: "Crawl depth"
                },
                parent_url: {
                    bsonType: "string",
                    description: "Parent URL"
                },
                links_found: {
                    bsonType: "int",
                    description: "Number of links found"
                },
                context: {
                    bsonType: "object",
                    description: "Additional context"
                }
            }
        }
    }
});

// Indexes for crawling_logs
db.crawling_logs.createIndex({ "session_id": 1, "timestamp": -1 });
db.crawling_logs.createIndex({ "investigation_id": 1, "timestamp": -1 });
db.crawling_logs.createIndex({ "level": 1, "timestamp": -1 });
db.crawling_logs.createIndex({ "timestamp": -1 });
db.crawling_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 7776000 });

// ============================================================================
// ERROR LOGS COLLECTION
// ============================================================================
// System-wide error tracking and debugging

db.createCollection("error_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "error_type", "message"],
            properties: {
                timestamp: {
                    bsonType: "date",
                    description: "Error timestamp"
                },
                error_type: {
                    bsonType: "string",
                    description: "Type of error"
                },
                message: {
                    bsonType: "string",
                    description: "Error message"
                },
                severity: {
                    enum: ["low", "medium", "high", "critical"],
                    description: "Error severity"
                },
                stack_trace: {
                    bsonType: "string",
                    description: "Stack trace"
                },
                context: {
                    bsonType: "object",
                    description: "Error context"
                },
                user_id: {
                    bsonType: "string",
                    description: "User ID if applicable"
                },
                investigation_id: {
                    bsonType: "string",
                    description: "Investigation ID if applicable"
                },
                component: {
                    bsonType: "string",
                    description: "System component where error occurred"
                },
                request_id: {
                    bsonType: "string",
                    description: "Request ID for tracing"
                },
                resolved: {
                    bsonType: "bool",
                    description: "Whether error has been resolved"
                },
                resolution_notes: {
                    bsonType: "string",
                    description: "Notes on error resolution"
                }
            }
        }
    }
});

// Indexes for error_logs
db.error_logs.createIndex({ "timestamp": -1 });
db.error_logs.createIndex({ "error_type": 1, "timestamp": -1 });
db.error_logs.createIndex({ "severity": 1, "timestamp": -1 });
db.error_logs.createIndex({ "component": 1, "timestamp": -1 });
db.error_logs.createIndex({ "investigation_id": 1 });
db.error_logs.createIndex({ "resolved": 1, "timestamp": -1 });
db.error_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 15552000 }); // 180 days

// ============================================================================
// PERFORMANCE METRICS COLLECTION
// ============================================================================
// System performance monitoring data

db.createCollection("performance_metrics", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "metric_type"],
            properties: {
                timestamp: {
                    bsonType: "date",
                    description: "Metric timestamp"
                },
                metric_type: {
                    enum: ["cpu", "memory", "disk", "network", "database", "api", "scraper", "crawler"],
                    description: "Type of metric"
                },
                value: {
                    bsonType: "double",
                    description: "Metric value"
                },
                unit: {
                    bsonType: "string",
                    description: "Unit of measurement"
                },
                component: {
                    bsonType: "string",
                    description: "System component"
                },
                tags: {
                    bsonType: "array",
                    description: "Metric tags for filtering"
                },
                metadata: {
                    bsonType: "object",
                    description: "Additional metric data"
                }
            }
        }
    }
});

// Indexes for performance_metrics
db.performance_metrics.createIndex({ "timestamp": -1 });
db.performance_metrics.createIndex({ "metric_type": 1, "timestamp": -1 });
db.performance_metrics.createIndex({ "component": 1, "timestamp": -1 });
db.performance_metrics.createIndex({ "tags": 1 });
db.performance_metrics.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 }); // 30 days

// ============================================================================
// RAW RESPONSES COLLECTION
// ============================================================================
// Store raw HTTP responses for analysis and replay

db.createCollection("raw_responses", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["job_id", "url", "timestamp"],
            properties: {
                job_id: {
                    bsonType: "string",
                    description: "Scraping job ID"
                },
                investigation_id: {
                    bsonType: "string",
                    description: "Investigation ID"
                },
                url: {
                    bsonType: "string",
                    description: "Request URL"
                },
                method: {
                    bsonType: "string",
                    description: "HTTP method"
                },
                timestamp: {
                    bsonType: "date",
                    description: "Response timestamp"
                },
                status_code: {
                    bsonType: "int",
                    description: "HTTP status code"
                },
                headers: {
                    bsonType: "object",
                    description: "Response headers"
                },
                body: {
                    bsonType: "string",
                    description: "Response body"
                },
                response_time: {
                    bsonType: "double",
                    description: "Response time in ms"
                },
                content_type: {
                    bsonType: "string",
                    description: "Content type"
                },
                content_length: {
                    bsonType: "int",
                    description: "Content length"
                },
                request_headers: {
                    bsonType: "object",
                    description: "Request headers"
                },
                cookies: {
                    bsonType: "object",
                    description: "Cookies"
                }
            }
        }
    }
});

// Indexes for raw_responses
db.raw_responses.createIndex({ "job_id": 1, "timestamp": -1 });
db.raw_responses.createIndex({ "investigation_id": 1, "timestamp": -1 });
db.raw_responses.createIndex({ "url": 1 });
db.raw_responses.createIndex({ "timestamp": -1 });
db.raw_responses.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 }); // 30 days

// ============================================================================
// SESSION DATA COLLECTION
// ============================================================================
// User session and temporary data storage

db.createCollection("session_data", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["session_id", "user_id", "created_at"],
            properties: {
                session_id: {
                    bsonType: "string",
                    description: "Session identifier"
                },
                user_id: {
                    bsonType: "string",
                    description: "User UUID"
                },
                created_at: {
                    bsonType: "date",
                    description: "Session creation time"
                },
                last_activity: {
                    bsonType: "date",
                    description: "Last activity timestamp"
                },
                ip_address: {
                    bsonType: "string",
                    description: "User IP address"
                },
                user_agent: {
                    bsonType: "string",
                    description: "User agent string"
                },
                data: {
                    bsonType: "object",
                    description: "Session data"
                },
                active: {
                    bsonType: "bool",
                    description: "Session active status"
                }
            }
        }
    }
});

// Indexes for session_data
db.session_data.createIndex({ "session_id": 1 }, { unique: true });
db.session_data.createIndex({ "user_id": 1, "last_activity": -1 });
db.session_data.createIndex({ "active": 1, "last_activity": -1 });
db.session_data.createIndex({ "created_at": 1 }, { expireAfterSeconds: 2592000 }); // 30 days

// ============================================================================
// API REQUEST LOGS COLLECTION
// ============================================================================
// Log all API requests for analytics and debugging

db.createCollection("api_request_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "method", "endpoint"],
            properties: {
                timestamp: {
                    bsonType: "date",
                    description: "Request timestamp"
                },
                request_id: {
                    bsonType: "string",
                    description: "Unique request ID"
                },
                user_id: {
                    bsonType: "string",
                    description: "User ID"
                },
                api_key_id: {
                    bsonType: "string",
                    description: "API key ID if used"
                },
                method: {
                    bsonType: "string",
                    description: "HTTP method"
                },
                endpoint: {
                    bsonType: "string",
                    description: "API endpoint"
                },
                path: {
                    bsonType: "string",
                    description: "Full request path"
                },
                query_params: {
                    bsonType: "object",
                    description: "Query parameters"
                },
                request_body: {
                    bsonType: "object",
                    description: "Request body"
                },
                response_status: {
                    bsonType: "int",
                    description: "Response status code"
                },
                response_time: {
                    bsonType: "double",
                    description: "Response time in ms"
                },
                ip_address: {
                    bsonType: "string",
                    description: "Client IP"
                },
                user_agent: {
                    bsonType: "string",
                    description: "User agent"
                },
                error: {
                    bsonType: "object",
                    description: "Error details if any"
                }
            }
        }
    }
});

// Indexes for api_request_logs
db.api_request_logs.createIndex({ "timestamp": -1 });
db.api_request_logs.createIndex({ "user_id": 1, "timestamp": -1 });
db.api_request_logs.createIndex({ "endpoint": 1, "timestamp": -1 });
db.api_request_logs.createIndex({ "response_status": 1, "timestamp": -1 });
db.api_request_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 7776000 }); // 90 days

// ============================================================================
// WEBHOOK EVENTS COLLECTION
// ============================================================================
// Store webhook events from external services

db.createCollection("webhook_events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "source", "event_type"],
            properties: {
                timestamp: {
                    bsonType: "date",
                    description: "Event timestamp"
                },
                source: {
                    bsonType: "string",
                    description: "Webhook source"
                },
                event_type: {
                    bsonType: "string",
                    description: "Event type"
                },
                payload: {
                    bsonType: "object",
                    description: "Event payload"
                },
                headers: {
                    bsonType: "object",
                    description: "Request headers"
                },
                signature: {
                    bsonType: "string",
                    description: "Webhook signature"
                },
                verified: {
                    bsonType: "bool",
                    description: "Signature verification status"
                },
                processed: {
                    bsonType: "bool",
                    description: "Processing status"
                },
                processing_error: {
                    bsonType: "string",
                    description: "Processing error if any"
                }
            }
        }
    }
});

// Indexes for webhook_events
db.webhook_events.createIndex({ "timestamp": -1 });
db.webhook_events.createIndex({ "source": 1, "timestamp": -1 });
db.webhook_events.createIndex({ "event_type": 1, "timestamp": -1 });
db.webhook_events.createIndex({ "processed": 1, "timestamp": -1 });
db.webhook_events.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 7776000 }); // 90 days

// ============================================================================
// NOTIFICATION QUEUE COLLECTION
// ============================================================================
// Queue for async notifications

db.createCollection("notification_queue", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["created_at", "notification_type", "recipient"],
            properties: {
                created_at: {
                    bsonType: "date",
                    description: "Queue entry timestamp"
                },
                notification_type: {
                    enum: ["email", "slack", "webhook", "sms", "push"],
                    description: "Notification type"
                },
                recipient: {
                    bsonType: "string",
                    description: "Recipient identifier"
                },
                subject: {
                    bsonType: "string",
                    description: "Notification subject"
                },
                message: {
                    bsonType: "string",
                    description: "Notification message"
                },
                data: {
                    bsonType: "object",
                    description: "Additional notification data"
                },
                priority: {
                    enum: ["low", "medium", "high", "urgent"],
                    description: "Notification priority"
                },
                status: {
                    enum: ["pending", "sent", "failed", "cancelled"],
                    description: "Notification status"
                },
                attempts: {
                    bsonType: "int",
                    description: "Delivery attempts"
                },
                sent_at: {
                    bsonType: "date",
                    description: "Sent timestamp"
                },
                error: {
                    bsonType: "string",
                    description: "Error message if failed"
                }
            }
        }
    }
});

// Indexes for notification_queue
db.notification_queue.createIndex({ "status": 1, "priority": -1, "created_at": 1 });
db.notification_queue.createIndex({ "created_at": -1 });
db.notification_queue.createIndex({ "notification_type": 1, "status": 1 });
db.notification_queue.createIndex({ "created_at": 1 }, { expireAfterSeconds: 2592000 }); // 30 days

// ============================================================================
// CACHE COLLECTION
// ============================================================================
// Application-level caching

db.createCollection("cache", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["key", "value", "created_at"],
            properties: {
                key: {
                    bsonType: "string",
                    description: "Cache key"
                },
                value: {
                    description: "Cached value (any type)"
                },
                created_at: {
                    bsonType: "date",
                    description: "Cache entry creation time"
                },
                expires_at: {
                    bsonType: "date",
                    description: "Expiration timestamp"
                },
                tags: {
                    bsonType: "array",
                    description: "Cache tags for bulk invalidation"
                }
            }
        }
    }
});

// Indexes for cache
db.cache.createIndex({ "key": 1 }, { unique: true });
db.cache.createIndex({ "tags": 1 });
db.cache.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

// ============================================================================
// Print success message
// ============================================================================

print("MongoDB collections created successfully!");
print("Collections created:");
print("  - scraping_logs");
print("  - crawling_logs");
print("  - error_logs");
print("  - performance_metrics");
print("  - raw_responses");
print("  - session_data");
print("  - api_request_logs");
print("  - webhook_events");
print("  - notification_queue");
print("  - cache");
