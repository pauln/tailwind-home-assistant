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

This will result in the "Tailwind iQ3" integration appearing on your HACS integrations dashboard; from there, click the "Install" button and confirm.
Once installed, HACS will list the integration as "pending restart" until you restart Home Assistant.

After restarting Home Assistant, you should get a notification within Home Assistant that a new device has been discovered.  Following the prompt to "check it out" (or manually navigating to the Integrations page), a "Tailwind iQ3" card should appear; click the "Configure" button, select how many doors you have set up, give it a name (if desired) and click "submit".

If your Tailwind iQ3 isn't automatically discovered (or you've "ignored" it), you can manually add the Tailwind iQ3 integration using the "Add Integration" button on the Integrations page in Home Assistant.  You'll need to enter the IP address of your iQ3 in addition to the number of doors (and optional name) as part of the manual setup process.