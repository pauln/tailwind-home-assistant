# tailwind-home-assistant
Tailwind iQ3 integration for Home Assistant

This integration is not final, and currently requires your Tailwind iQ3 device to be running beta firmware.

The integration will create one or more Cover entities for your garage door(s).
The state (open/closed) is updated every 10 seconds via local polling - no cloud connection is required.

# Installation
For the best experience, install via [HACS](https://hacs.xyz/).
At this stage, you'll need to [add it to HACS as a custom repository](https://hacs.xyz/docs/faq/custom_repositories) using the following details:
- Repository URL: `https://github.com/pauln/tailwind-home-assistant`
- Category: `Integration`
