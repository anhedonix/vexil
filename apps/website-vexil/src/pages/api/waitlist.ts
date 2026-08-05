import type { APIRoute } from "astro";
import { Resend } from "resend";
import {
  RESEND_API_KEY,
  RESEND_FROM_EMAIL,
  RESEND_TO_EMAIL,
} from "astro:env/server";
import { buildInternalWaitlistEmail } from "../../lib/waitlist-emails";

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

export const POST: APIRoute = async ({ request }) => {
  if (!RESEND_API_KEY || !RESEND_FROM_EMAIL || !RESEND_TO_EMAIL) {
    return json(
      { ok: false, error: "Email service is not configured on the server." },
      503,
    );
  }

  let payload: { email?: unknown; userType?: unknown; comments?: unknown };
  try {
    payload = await request.json();
  } catch {
    return json({ ok: false, error: "Invalid request payload." }, 400);
  }

  const email = typeof payload.email === "string" ? payload.email.trim() : "";
  const userType =
    typeof payload.userType === "string" ? payload.userType.trim() : "";
  const comments =
    typeof payload.comments === "string" ? payload.comments.trim() : "";

  if (!EMAIL_RE.test(email)) {
    return json(
      { ok: false, error: "Please provide a valid email address." },
      400,
    );
  }
  if (
    userType !== "individual" &&
    userType !== "studio" &&
    userType !== "hobbyist"
  ) {
    return json(
      { ok: false, error: "Please select who you are representing." },
      400,
    );
  }

  const userTypeLabel =
    userType === "individual"
      ? "Individual Artist / Freelancer"
      : userType === "studio"
        ? "Studio / Team"
        : "Hobbyist / Interested";

  const { subject, text, html } = buildInternalWaitlistEmail({
    email,
    userTypeLabel,
    comments,
  });

  const resend = new Resend(RESEND_API_KEY);
  const { error } = await resend.emails.send({
    from: RESEND_FROM_EMAIL,
    to: RESEND_TO_EMAIL,
    replyTo: email,
    subject,
    text,
    html,
  });

  if (error) {
    console.error("Resend send failed:", error);
    return json(
      { ok: false, error: "Could not deliver your message. Please try again." },
      502,
    );
  }

  return json({ ok: true });
};
