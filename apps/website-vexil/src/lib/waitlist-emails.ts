const WORDMARK_URL = 'https://vexil.tools/vexil-wordmark.png';
const SITE_URL = 'https://vexil.tools';

const FONT_SANS =
  "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
const FONT_MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

export const escapeHtml = (s: string) =>
  s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

export type InternalWaitlistEmailInput = {
  email: string;
  userTypeLabel: string;
  comments: string;
};

export type WaitlistEmailContent = {
  subject: string;
  text: string;
  html: string;
};

export function buildInternalWaitlistEmail({
  email,
  userTypeLabel,
  comments,
}: InternalWaitlistEmailInput): WaitlistEmailContent {
  const commentsDisplay = comments || '(none)';
  const safeEmail = escapeHtml(email);
  const safeType = escapeHtml(userTypeLabel);
  const safeComments = escapeHtml(commentsDisplay);

  const subject = `New VEXiL waitlist signup - ${email}`;

  const text = [
    'New VEXiL waitlist application',
    '',
    `Email: ${email}`,
    `Type:  ${userTypeLabel}`,
    '',
    'Comments:',
    commentsDisplay,
    '',
    `— VEXiL · ${SITE_URL}`,
  ].join('\n');

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="light" />
  <title>${escapeHtml(subject)}</title>
</head>
<body style="margin:0;padding:0;background-color:#efeff0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#efeff0;">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:560px;background-color:#ffffff;border:1px solid #bcbcbd;border-radius:4px;">
          <tr>
            <td style="padding:32px 32px 24px 32px;">
              <img src="${WORDMARK_URL}" width="140" alt="VEXiL" style="display:block;width:140px;height:auto;border:0;outline:none;text-decoration:none;" />
            </td>
          </tr>
          <tr>
            <td style="padding:0 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="height:2px;line-height:2px;font-size:0;background-color:#2e97f2;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 32px 8px 32px;">
              <h1 style="margin:0;font-family:${FONT_SANS};font-size:18px;font-weight:500;line-height:1.4;color:#252526;letter-spacing:-0.02em;">
                New waitlist application
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 32px 8px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
                <tr>
                  <td style="padding:8px 16px 8px 0;width:88px;vertical-align:top;font-family:${FONT_SANS};font-size:12px;font-weight:400;line-height:1.5;color:#6b7280;">
                    Email
                  </td>
                  <td style="padding:8px 0;vertical-align:top;font-family:${FONT_MONO};font-size:14px;font-weight:400;line-height:1.5;color:#252526;">
                    ${safeEmail}
                  </td>
                </tr>
                <tr>
                  <td style="padding:8px 16px 8px 0;width:88px;vertical-align:top;font-family:${FONT_SANS};font-size:12px;font-weight:400;line-height:1.5;color:#6b7280;border-top:1px solid #efeff0;">
                    Type
                  </td>
                  <td style="padding:8px 0;vertical-align:top;font-family:${FONT_SANS};font-size:14px;font-weight:400;line-height:1.5;color:#252526;border-top:1px solid #efeff0;">
                    ${safeType}
                  </td>
                </tr>
                <tr>
                  <td style="padding:8px 16px 8px 0;width:88px;vertical-align:top;font-family:${FONT_SANS};font-size:12px;font-weight:400;line-height:1.5;color:#6b7280;border-top:1px solid #efeff0;">
                    Comments
                  </td>
                  <td style="padding:8px 0;vertical-align:top;font-family:${FONT_SANS};font-size:14px;font-weight:400;line-height:1.5;color:#252526;border-top:1px solid #efeff0;white-space:pre-wrap;">
                    ${safeComments}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 32px 32px 32px;">
              <p style="margin:0;font-family:${FONT_SANS};font-size:12px;font-weight:400;line-height:1.5;color:#6b7280;">
                VEXiL · <a href="${SITE_URL}" style="color:#2e97f2;text-decoration:none;">${SITE_URL.replace('https://', '')}</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

  return { subject, text, html };
}
