import type { APIRoute } from 'astro';
import { Resend } from 'resend';
import {
  RESEND_API_KEY,
  RESEND_FROM_EMAIL,
  RESEND_TO_EMAIL,
} from 'astro:env/server';

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

export const POST: APIRoute = async ({ request }) => {
  if (!RESEND_API_KEY || !RESEND_FROM_EMAIL || !RESEND_TO_EMAIL) {
    return json(
      { ok: false, error: 'Email service is not configured on the server.' },
      503,
    );
  }

  let payload: { email?: unknown; userType?: unknown; comments?: unknown };
  try {
    payload = await request.json();
  } catch {
    return json({ ok: false, error: 'Invalid request payload.' }, 400);
  }

  const email = typeof payload.email === 'string' ? payload.email.trim() : '';
  const userType = typeof payload.userType === 'string' ? payload.userType.trim() : '';
  const comments =
    typeof payload.comments === 'string' ? payload.comments.trim().slice(0, 2000) : '';

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'Please provide a valid email address.' }, 400);
  }
  if (userType !== 'individual' && userType !== 'studio' && userType !== 'hobbyist') {
    return json({ ok: false, error: 'Please select who you are representing.' }, 400);
  }

  const userTypeLabel =
    userType === 'individual'
      ? 'Individual Artist / Freelancer'
      : userType === 'studio'
        ? 'Studio / Team'
        : 'Hobbyist / Interested';

  const text = [
    'New VEXiL waitlist application',
    '',
    `Email: ${email}`,
    `Type:  ${userTypeLabel}`,
    '',
    'Comments:',
    comments || '(none)',
  ].join('\n');

  const html = `
    <h2 style="margin:0 0 16px;font-family:system-ui,sans-serif">New VEXiL waitlist application</h2>
    <table style="font-family:system-ui,sans-serif;font-size:14px;border-collapse:collapse">
      <tr><td style="padding:4px 12px 4px 0;color:#666"><strong>Email</strong></td><td>${escapeHtml(email)}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;color:#666"><strong>Type</strong></td><td>${escapeHtml(userTypeLabel)}</td></tr>
    </table>
    <p style="font-family:system-ui,sans-serif;font-size:14px;color:#666;margin:16px 0 4px"><strong>Comments</strong></p>
    <pre style="white-space:pre-wrap;font-family:system-ui,sans-serif;font-size:14px;margin:0">${escapeHtml(comments || '(none)')}</pre>
  `;

  const resend = new Resend(RESEND_API_KEY);
  const { error } = await resend.emails.send({
    from: RESEND_FROM_EMAIL,
    to: RESEND_TO_EMAIL,
    replyTo: email,
    subject: `New VEXiL waitlist signup - ${email}`,
    text,
    html,
  });

  if (error) {
    console.error('Resend send failed:', error);
    return json({ ok: false, error: 'Could not deliver your message. Please try again.' }, 502);
  }

  return json({ ok: true });
};
