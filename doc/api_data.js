define({ "api": [
  {
    "type": "post",
    "url": "/attachments",
    "title": "Create Attachment",
    "name": "CreateAttachments",
    "group": "Attachments",
    "description": "<p>Create a new attachemnt [and attach to a test or run]</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit attachments per request</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of file</p>"
          },
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "data",
            "description": "<p>Base64 encoded data</p>"
          },
          {
            "group": "Request Body",
            "type": "Integer",
            "optional": true,
            "field": "run_id",
            "description": "<p>ID of run to attach file</p>"
          },
          {
            "group": "Request Body",
            "type": "Integer",
            "optional": true,
            "field": "test_id",
            "description": "<p>ID of test to attach file</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "{\n    \"name\": \"my_attachment.log\",\n    \"data\": \"aGVsbG8gd29ybGQ=\",\n    \"test_id\": 1,\n    \"run_id\": \"1\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n {\n      \"attachment_id\": 1,\n      \"name\": \"my_attachment.log\",\n      \"location\": \"https://storage101.dfw1.clouddrive.com/v1...\"\n }",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "post",
    "url": "/attachments/{attachment_id}/filter",
    "title": "Filter Attachment",
    "name": "FilterAttachment",
    "group": "Attachments",
    "description": "<p>Get list of matches using one or more filters Api can return 3 possible match types: group dictionaries, group lists, or string matches Also the api call will attempt a literal_eval and a json.loads on the values of groups, if not sucessful it will return the string</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          }
        ],
        "Parameters": [
          {
            "group": "Parameters",
            "type": "String",
            "allowedValues": [
              "\"groupdict\"",
              "\"groups\"",
              "\"match\""
            ],
            "optional": false,
            "field": "type",
            "description": "<p>Type of matching to perform, overrides auto discovery</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "List",
            "optional": false,
            "field": "List",
            "description": "<p>of filter names</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "[\n    \"somefilter_with_named_groups\",\n    \"somefilter_with_groups\",\n    \"somefilter_with_no_groups\"\n]",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "group_dict",
            "description": "<p>A dictionary based on named groups in regex</p>"
          },
          {
            "group": "Response Body",
            "type": "List",
            "optional": false,
            "field": "group_list",
            "description": "<p>A list of groups based on non named groups in regex</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example: type=None",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"named_group\": \"matched text that doesn't support literal_eval or json.loads\",\n        \"named_group2\": {\n            \"supported\": \"json.loads or literal_eval\"\n        },\n        \"named_group3\": [\n            \"another supported literal_eval/json.loads\"\n        ]\n    },\n    [\n        \"regex2 matched but only has non named groups\",\n        \"group2\",\n        \"group3\"\n    ],\n    \"regex3 match that had no groups returns a string match\"\n]",
          "type": "json"
        },
        {
          "title": "Response Example: type=groupdict",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"named_group\": \"matched text that doesn't support literal_eval or json.loads\",\n        \"named_group2\": {\n            \"supported\": \"json.loads or literal_eval\"\n        },\n        \"named_group3\": [\n            \"another supported literal_eval/json.loads\",\n            \"woo\"\n        ]\n    },\n    {},\n    {}\n]",
          "type": "json"
        },
        {
          "title": "Response Example: type=groups",
          "content": "HTTP/1.1 200 OK\n[\n [\"matched text that doesn't support literal_eval or json.loads\", {\"supported\": \"json.loads or literal_eval\"}, [\"another supported literal_eval/json.loads\"],\n [\"regex2 matched but only has non named groups\", \"group2\", \"group3\"],\n []\n]",
          "type": "json"
        },
        {
          "title": "Response Example: type=match",
          "content": "HTTP/1.1 200 OK\n[\n    \"matched text that doesn't support literal_eval or json.loads\\nsupported: json.loads or literal_eval\\n another supported literal_eval/json.loads\",\n    \"regex2 matched but only has non named groups:group2:group3\",\n    \"regex3 match that had no groups returns a string match\"\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "get",
    "url": "/attachments/{attachment_id}",
    "title": "Get Attachment by ID",
    "name": "GetAttachment",
    "group": "Attachments",
    "description": "<p>Get an attachment by attachment ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          }
        ],
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n     \"attachment_id\": \"1\",\n     \"name\": \"cafe.master.log\",\n     \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n }",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "get",
    "url": "/attachments/{attachment_id}/content",
    "title": "Get Attachment Content by ID",
    "name": "GetAttachmentContent",
    "group": "Attachments",
    "description": "<p>Get an attachment's content by attachment ID Note: This call redirects to location URL</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          }
        ],
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "Binary",
            "optional": false,
            "field": "Attachment",
            "description": "<p>Content</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "hello world",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "get",
    "url": "/attachments",
    "title": "Get Attachments",
    "name": "GetAttachments",
    "group": "Attachments",
    "description": "<p>Get a list of attachments</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit attachments per request</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[{\n     \"attachment_id\": \"1\",\n     \"name\": \"cafe.master.log\",\n     \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n },\n {\n     \"attachment_id\": \"2\",\n     \"name\": \"cafe.master.log\",\n     \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "get",
    "url": "/runs/{run_id}/attachments",
    "title": "Get Attachments for run",
    "name": "GetRunAttachments",
    "group": "Attachments",
    "description": "<p>Get attachments by run ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID of run</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"attachment_id\": \"1\",\n        \"name\": \"cafe.master.log\",\n        \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n    },\n    {\n        \"attachment_id\": \"2\",\n        \"name\": \"cafe.master.log\",\n        \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/runs.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "get",
    "url": "/tests/{test_id}/attachments",
    "title": "Get Attachments for test",
    "name": "GetTestAttachments",
    "group": "Attachments",
    "description": "<p>Get attachments by Test ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "test_id",
            "description": "<p>Test ID of test</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"attachment_id\": \"1\",\n        \"name\": \"cafe.master.log\",\n        \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n    },\n    {\n        \"attachment_id\": \"2\",\n        \"name\": \"cafe.master.log\",\n        \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/tests.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "put",
    "url": "/attachments",
    "title": "Update Attachment",
    "name": "UpdateAttachments",
    "group": "Attachments",
    "description": "<p>Update an attachemnt [and attach to a test or run]</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit attachments per request</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Request Body",
            "type": "String",
            "optional": true,
            "field": "name",
            "description": "<p>Name of file</p>"
          },
          {
            "group": "Request Body",
            "type": "String",
            "optional": true,
            "field": "data",
            "description": "<p>Base64 encoded data</p>"
          },
          {
            "group": "Request Body",
            "type": "Integer",
            "optional": true,
            "field": "run_id",
            "description": "<p>ID of run to attach file</p>"
          },
          {
            "group": "Request Body",
            "type": "Integer",
            "optional": true,
            "field": "test_id",
            "description": "<p>ID of test to attach file</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "{\n    \"attachment_id\": 15,\n    \"name\": \"my_attachment.log\",\n    \"data\": \"aGVsbG8gd29ybGQ=\",\n    \"test_id\": 1,\n    \"run_id\": \"1\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "attachment_id",
            "description": "<p>Attachment_id of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of attachment</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "location",
            "description": "<p>Location of attachment</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"attachment_id\": 15,\n    \"name\": \"my_attachment.log\",\n    \"location\": \"https://storage101.dfw1.clouddrive.com/v1/...\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Attachments"
  },
  {
    "type": "post",
    "url": "/attachments/filters",
    "title": "Create Filter",
    "name": "CreateFilter",
    "group": "Filters",
    "description": "<p>Create a filter</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Filters"
  },
  {
    "type": "get",
    "url": "/attachments/filters/{name}",
    "title": "Get Filter by name",
    "name": "GetAttachmentFilter",
    "group": "Filters",
    "description": "<p>Get an Filter by name</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Filter name</p>"
          }
        ],
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Filters"
  },
  {
    "type": "get",
    "url": "/attachments/filters",
    "title": "Get Filters",
    "name": "GetAttachmentFilters",
    "group": "Filters",
    "description": "<p>Get a list of regex filters and names</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Filters"
  },
  {
    "type": "put",
    "url": "/attachments/filters",
    "title": "Update Filter",
    "name": "UpdateAttachmentFilters",
    "group": "Filters",
    "description": "<p>Update a filter</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Request Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "regex",
            "description": "<p>Regex filter</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Name of filter</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"regex\": \".*\",\n    \"name\": \"somefilter\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/attachments.py",
    "groupTitle": "Filters"
  },
  {
    "type": "post",
    "url": "/runs",
    "title": "Create Run",
    "name": "CreateRun",
    "group": "Runs",
    "description": "<p>Create a new run</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "type": "String",
            "optional": true,
            "field": "run_at",
            "description": "<p>DateTimeStamp or run start time</p>"
          },
          {
            "group": "Request Body",
            "type": "Float",
            "optional": true,
            "field": "run_time",
            "description": "<p>Run time in seconds</p>"
          },
          {
            "group": "Request Body",
            "type": "Dictionary",
            "optional": true,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "{\n    \"run_at\": \"2016-06-08T03:26:29+00:00\",\n    \"run_time\": 234785.27076625824,\n    \"metadata\": {\n        \"engine\": \"opencafe\",\n        \"product\": \"cbs\",\n        \"build_version\": \"2.1\",\n        \"datacenter\": \"dfw1\"\n    }\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "skipped",
            "description": "<p>Number of skipped tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "failed",
            "description": "<p>Number of failed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "passed",
            "description": "<p>Number of passed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_id",
            "description": "<p>ID of run</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_at",
            "description": "<p>DateTimeStamp or run start time</p>"
          },
          {
            "group": "Response Body",
            "type": "Float",
            "optional": false,
            "field": "run_time",
            "description": "<p>Run time in seconds</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n {\n     \"skipped\": 0,\n     \"run_id\": 1,\n     \"run_at\": \"2016-06-08T03:26:29+00:00\",\n     \"failed\": 0,\n     \"run_time\": 234785.27076625824,\n     \"passed\": 0,\n     \"metadata\": {\n         \"engine\": \"opencafe\",\n         \"build_version\": \"2.1\",\n         \"product\": \"cbs\",\n         \"datacenter\": \"dfw1\"\n     }\n }",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/runs.py",
    "groupTitle": "Runs"
  },
  {
    "type": "get",
    "url": "/runs/{run_id}",
    "title": "Get Run by ID",
    "name": "GetRun",
    "group": "Runs",
    "description": "<p>Get a run by ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID of run</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "skipped",
            "description": "<p>Number of skipped tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "failed",
            "description": "<p>Number of failed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "passed",
            "description": "<p>Number of passed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_id",
            "description": "<p>ID of run</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_at",
            "description": "<p>DateTimeStamp or run start time</p>"
          },
          {
            "group": "Response Body",
            "type": "Float",
            "optional": false,
            "field": "run_time",
            "description": "<p>Run time in seconds</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"skipped\": 1,\n    \"run_id\": \"1015\",\n    \"run_at\": \"2016-06-08T03:26:29+00:00\",\n    \"failed\": 0,\n    \"run_time\": 234785.27076625824,\n    \"passed\": 1757,\n    \"metadata\": {\n        \"engine\": \"opencafe\",\n        \"product\": \"cbs\",\n        \"build_version\": \"2.1\",\n        \"datacenter\": \"dfw1\"\n    }\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/runs.py",
    "groupTitle": "Runs"
  },
  {
    "type": "get",
    "url": "/runs",
    "title": "Get Runs",
    "name": "GetRuns",
    "group": "Runs",
    "description": "<p>Get a list of runs</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit runs per request</p>"
          },
          {
            "group": "Parameters",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test based on failed test count</p>"
          },
          {
            "group": "Parameters",
            "type": "Metadata",
            "optional": false,
            "field": "metadata",
            "description": "<p>All other params read as metadata key=value used to filter runs</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "skipped",
            "description": "<p>Number of skipped tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "failed",
            "description": "<p>Number of failed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "passed",
            "description": "<p>Number of passed tests</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_id",
            "description": "<p>ID of run</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_at",
            "description": "<p>DateTimeStamp or run start time</p>"
          },
          {
            "group": "Response Body",
            "type": "Float",
            "optional": false,
            "field": "run_time",
            "description": "<p>Run time in seconds</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"skipped\": 1,\n        \"run_id\": \"1015\",\n        \"run_at\": \"2016-06-08T03:26:29+00:00\",\n        \"failed\": 0,\n        \"run_time\": 234785.27076625824,\n        \"passed\": 1757,\n        \"metadata\": {\n            \"engine\": \"opencafe\",\n            \"product\": \"cbs\",\n            \"build_version\": \"2.1\",\n            \"datacenter\": \"dfw1\"\n        }\n    },\n    {\n        \"skipped\": 2,\n        \"run_id\": \"964\",\n        \"run_at\": \"2016-06-04T17:20:28+00:00\",\n        \"failed\": 1,\n        \"run_time\": 193982.4073586464,\n        \"passed\": 1755,\n        \"metadata\": {\n            \"engine\": \"opencafe\",\n            \"product\": \"compute\",\n            \"build_version\": \"3.1\",\n            \"datacenter\": \"ord\"\n        }\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/runs.py",
    "groupTitle": "Runs"
  },
  {
    "type": "get",
    "url": "/status/{test_name}",
    "title": "Get stats by test name",
    "name": "GetStatsByName",
    "group": "Stats",
    "description": "<p>Get stats by test name</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Name of test</p>"
          }
        ],
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "failed",
            "description": "<p>Number of failed test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "passed",
            "description": "<p>Number of passed test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "skipped",
            "description": "<p>Number of skipped test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_count",
            "description": "<p>Number of times test ran</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Test Name</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"failed\": \"1\",\n    \"passed\": \"1107\",\n    \"run_count\": \"1108\",\n    \"skipped\": \"0\",\n    \"test_name\": \"somerepo.ProfileTest.test_profile_find_by_name\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/stats.py",
    "groupTitle": "Stats"
  },
  {
    "type": "get",
    "url": "/tests/{test_id}/stats",
    "title": "Get stats by test ID",
    "name": "GetTestStatsByID",
    "group": "Stats",
    "description": "<p>Get test stats by ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "failed",
            "description": "<p>Number of failed test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "passed",
            "description": "<p>Number of passed test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "skipped",
            "description": "<p>Number of skipped test runs</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "run_count",
            "description": "<p>Number of times test ran</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Test Name</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"failed\": \"1\",\n    \"passed\": \"1107\",\n    \"run_count\": \"1108\",\n    \"skipped\": \"0\",\n    \"test_name\": \"somerepo.ProfileTest.test_profile_find_by_name\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/tests.py",
    "groupTitle": "Stats"
  },
  {
    "type": "get",
    "url": "/tests",
    "title": "Create Test",
    "name": "CreateTest",
    "group": "Tests",
    "description": "<p>Create a test and add to a run</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Metadata",
            "optional": false,
            "field": "metadata",
            "description": "<p>All other params read as metadata key=value used to filter tests</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\"",
              "\"skipped\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID, same at URL run_id</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "start_time",
            "description": "<p>DateTimeStamp or test start time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "stop_time",
            "description": "<p>DateTimeStamp or test stop time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Name of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "test_id",
            "description": "<p>Test ID</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": true,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-24T17:18:35+00:00\",\n        \"stop_time\": \"2014-03-24T17:18:35.060518+00:00\",\n        \"test_name\": \"somerepo.ClusterActionTest.test_do_detach_policy_missing_policy\",\n        \"test_id\": \"3517\",\n        \"metadata\": {\n            \"tags\": \"worker-5\"\n        }\n    },\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-23T22:58:31+00:00\",\n        \"stop_time\": \"2014-03-23T22:58:31.052204+00:00\",\n        \"test_name\": \"somerepo.PolicyControllerTest.test_policy_update_normal\",\n        \"test_id\": \"3518\",\n        \"metadata\": {\n            \"tags\": \"worker-7\"\n        }\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/tests.py",
    "groupTitle": "Tests"
  },
  {
    "type": "get",
    "url": "/runs/{run_id}/tests",
    "title": "Get Tests by run ID",
    "name": "GetRunTests",
    "group": "Tests",
    "description": "<p>Get all tests for a given run ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit runs per request</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "name",
            "description": "<p>Regex name filter</p>"
          },
          {
            "group": "Parameters",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\"",
              "\"skipped\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test</p>"
          }
        ],
        "URL Variable": [
          {
            "group": "URL Variable",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID of run</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\"",
              "\"skipped\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID, same at URL run_id</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "start_time",
            "description": "<p>DateTimeStamp or test start time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "stop_time",
            "description": "<p>DateTimeStamp or test stop time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Name of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "test_id",
            "description": "<p>Test ID</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-24T17:18:35+00:00\",\n        \"stop_time\": \"2014-03-24T17:18:35.060518+00:00\",\n        \"test_name\": \"somerepo.ClusterActionTest.test_do_detach_policy_missing_policy\",\n        \"test_id\": \"3517\",\n        \"metadata\": {\n            \"tags\": \"worker-5\"\n        }\n    },\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-23T22:58:31+00:00\",\n        \"stop_time\": \"2014-03-23T22:58:31.052204+00:00\",\n        \"test_name\": \"somerepo.PolicyControllerTest.test_policy_update_normal\",\n        \"test_id\": \"3518\",\n        \"metadata\": {\n            \"tags\": \"worker-7\"\n        }\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/runs.py",
    "groupTitle": "Tests"
  },
  {
    "type": "get",
    "url": "/tests/{test_id}",
    "title": "Get Test by ID",
    "name": "GetTest",
    "group": "Tests",
    "description": "<p>Get test by ID</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\"",
              "\"skipped\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID, same at URL run_id</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "start_time",
            "description": "<p>DateTimeStamp or test start time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "stop_time",
            "description": "<p>DateTimeStamp or test stop time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Name of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "test_id",
            "description": "<p>Test ID</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n{\n    \"status\": \"passed\",\n    \"run_id\": \"3\",\n    \"start_time\": \"2014-03-24T17:18:35+00:00\",\n    \"stop_time\": \"2014-03-24T17:18:35.060518+00:00\",\n    \"test_name\": \"somerepo.ClusterActionTest.test_do_detach_policy_missing_policy\",\n    \"test_id\": \"3517\",\n    \"metadata\": {\n        \"tags\": \"worker-5\"\n    }\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/tests.py",
    "groupTitle": "Tests"
  },
  {
    "type": "get",
    "url": "/tests",
    "title": "Get Tests",
    "name": "GetTests",
    "group": "Tests",
    "description": "<p>Get a list of tests</p>",
    "header": {
      "fields": {
        "Headers": [
          {
            "group": "Headers",
            "type": "String",
            "optional": false,
            "field": "X-Auth-Token",
            "description": "<p>Identity Token with api access</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameters": [
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-",
            "optional": true,
            "field": "page",
            "defaultValue": "1",
            "description": "<p>Page number to start on</p>"
          },
          {
            "group": "Parameters",
            "type": "Integer",
            "size": "1-1000",
            "optional": true,
            "field": "limit",
            "defaultValue": "100",
            "description": "<p>Limit runs per request</p>"
          },
          {
            "group": "Parameters",
            "type": "Metadata",
            "optional": false,
            "field": "metadata",
            "description": "<p>All other params read as metadata key=value used to filter tests</p>"
          }
        ],
        "Request Body": [
          {
            "group": "Request Body",
            "optional": false,
            "field": "None",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example:",
          "content": "None",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Response Body": [
          {
            "group": "Response Body",
            "type": "String",
            "allowedValues": [
              "\"passed\"",
              "\"failed\"",
              "\"skipped\""
            ],
            "optional": false,
            "field": "status",
            "description": "<p>Status of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "run_id",
            "description": "<p>Run ID, same at URL run_id</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "start_time",
            "description": "<p>DateTimeStamp or test start time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "stop_time",
            "description": "<p>DateTimeStamp or test stop time</p>"
          },
          {
            "group": "Response Body",
            "type": "String",
            "optional": false,
            "field": "test_name",
            "description": "<p>Name of test</p>"
          },
          {
            "group": "Response Body",
            "type": "Integer",
            "optional": false,
            "field": "test_id",
            "description": "<p>Test ID</p>"
          },
          {
            "group": "Response Body",
            "type": "Dictionary",
            "optional": false,
            "field": "metadata",
            "description": "<p>Dictionary containing metadata key value pairs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Response Example:",
          "content": "HTTP/1.1 200 OK\n[\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-24T17:18:35+00:00\",\n        \"stop_time\": \"2014-03-24T17:18:35.060518+00:00\",\n        \"test_name\": \"somerepo.ClusterActionTest.test_do_detach_policy_missing_policy\",\n        \"test_id\": \"3517\",\n        \"metadata\": {\n            \"tags\": \"worker-5\"\n        }\n    },\n    {\n        \"status\": \"passed\",\n        \"run_id\": \"3\",\n        \"start_time\": \"2014-03-23T22:58:31+00:00\",\n        \"stop_time\": \"2014-03-23T22:58:31.052204+00:00\",\n        \"test_name\": \"somerepo.PolicyControllerTest.test_policy_update_normal\",\n        \"test_id\": \"3518\",\n        \"metadata\": {\n            \"tags\": \"worker-7\"\n        }\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./myapp/api/tests.py",
    "groupTitle": "Tests"
  },
  {
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "optional": false,
            "field": "varname1",
            "description": "<p>No type.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "varname2",
            "description": "<p>With type.</p>"
          }
        ]
      }
    },
    "type": "",
    "url": "",
    "version": "0.0.0",
    "filename": "./doc/main.js",
    "group": "_home_nath4854_code_metrics_metricsandstuff_doc_main_js",
    "groupTitle": "_home_nath4854_code_metrics_metricsandstuff_doc_main_js",
    "name": ""
  }
] });
