# Sesshu

This project provides distributed data collection support for Panorama. Currently, only Amazon SQS and Amazon SNS is supported for job distribution and results.

## Disclaimer

This code is so pre-alpha it hurts; expect problems! :fire:

## Dependencies

The following Python packages are required for Sesshu to function correctly:

* `bs4` - Processing of HTML.
* `click` - Command-line argument processing.
* `boto3` - Amazon AWS integration.
* `requests` - HTTP request library.
* `cerberus` - Validation of messages and other documents.

Once these modules are installed, a valid configuration file is required. See the **Configuration** section for more information.

## Configuration

The configuration for Sesshu is performed via a YAML document - named `sesshu.yaml` by default. An example configuration ships with Sesshu and is named `esshu.dist.yaml`.

### AWS API

Currently, Sesshu assumes that `boto3` is able to enumerate credentials to access the configured SNS and SQS resources without intervention. This may be via `~/.aws/credentials` file, IAM Instance Profiles (recommended), environment variables, or otherwise. This is done to encourage the use of IAM Instance Profiles, rather than generating AWS access keys and placing them into unencrypted text files.

There is currently no ability to provide AWS access keys directly.

### Queuing (SNS -> SQS)

SNS and SQS are used for request and response distribution.

The configuration of a re-drive policy and a dead-letter queue after a sane number of retries is recommended for handling messages that are rejected by the worker(s). This is in order to safely remove malformed messages out of the queue with a minimal number of re-fetches.

## Modules

Simply put, modules provide data collection for a given target. These modules are invoked by Sesshu when a valid `request` message is retrieved from the input message queue.

The module to invoke is specified by the request message itself, but in order to work, must be installed and configured.

### Security

As Sesshu modules dispatch the input to a given plugin and return results, there are no security controls implemented in the Sesshu framework (past validation of the input message schema).

As an example, the `http_` modules simply perform an HTTP request against the requested URL and return the relevant data. There is no URL filtering, or security controls inside of these example modules (such as filtering against SSRF attacks, etc). This was done as some modules (not published) require access to these 'private' URLs, such as the Amazon EC2 meta-data service, etc.

If this is a concern - which it should be if accepting URLs from users - security controls would need to be implemented before submission of messages onto the queue.

### Installation

Installation and configuration of a new module can be performed in the following manner:

1. Install required Python dependencies for the new module.
2. Install the module file into the `sesshu/plugin/` directory.
3. Add the module into `sesshu.plugin` as an import inside of `__init__`.
4. Add the new module into the Sesshu configuration - under the `plugin` section.

### Results.

Result data should be output in a format that is serializable into JSON. A Python native `dict` or `list` is preferable here, if possible.

Module result data should *NOT* be serialized into JSON inside of the module, as results are added into a response document which contains both the target, and the module from which the data was generated. The response document itself will be serialized into JSON when the results are dispatched.
