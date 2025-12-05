# How to use Django’s Content Security Policy

<a id="csp-config"></a>

## Basic config

To enable Content Security Policy (CSP) in your Django project:

1. Add the CSP middleware to your [`MIDDLEWARE`](../ref/settings.md#std-setting-MIDDLEWARE) setting:
   ```default
   MIDDLEWARE = [
       # ...
       "django.middleware.csp.ContentSecurityPolicyMiddleware",
       # ...
   ]
   ```
2. Configure the CSP policies in your `settings.py` using either
   [`SECURE_CSP`](../ref/settings.md#std-setting-SECURE_CSP) or [`SECURE_CSP_REPORT_ONLY`](../ref/settings.md#std-setting-SECURE_CSP_REPORT_ONLY) (or both). The
   [CSP Settings docs](../ref/csp.md#csp-settings) provide more details about the
   differences between these two:
   ```default
   from django.utils.csp import CSP

   # To enforce a CSP policy:
   SECURE_CSP = {
       "default-src": [CSP.SELF],
       # Add more directives to be enforced.
   }

   # Or for report-only mode:
   SECURE_CSP_REPORT_ONLY = {
       "default-src": [CSP.SELF],
       # Add more directives as needed.
       "report-uri": "/path/to/reports-endpoint/",
   }
   ```

<a id="csp-nonce-config"></a>

## Nonce config

To use nonces in your CSP policy, beside the basic config, you need to:

1. Include the [`NONCE`](../ref/csp.md#django.utils.csp.CSP.NONCE) placeholder value in the CSP
   settings. This only applies to `script-src` or `style-src` directives:
   ```default
   from django.utils.csp import CSP

   SECURE_CSP = {
       "default-src": [CSP.SELF],
       # Allow self-hosted scripts and script tags with matching `nonce` attr.
       "script-src": [CSP.SELF, CSP.NONCE],
       # Example of the less secure 'unsafe-inline' option.
       "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
   }
   ```
2. Add the [`csp()`](../ref/templates/api.md#django.template.context_processors.csp) context processor to
   your [`TEMPLATES`](../ref/settings.md#std-setting-TEMPLATES) setting. This makes the generated nonce value
   available in the Django templates as the `csp_nonce` context variable:
   ```default
   TEMPLATES = [
       {
           "BACKEND": "django.template.backends.django.DjangoTemplates",
           "OPTIONS": {
               "context_processors": [
                   # ...
                   "django.template.context_processors.csp",
               ],
           },
       },
   ]
   ```
3. In your templates, add the `nonce` attribute to the relevant inline
   `<style>` or `<script>` tags, using the `csp_nonce` context variable:
   ```html+django
   <style nonce="{{ csp_nonce }}">
     /* These inline styles will be allowed. */
   </style>

   <script nonce="{{ csp_nonce }}">
     // This inline JavaScript will be allowed.
   </script>
   ```
