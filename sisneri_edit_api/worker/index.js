
export default {
  async fetch(req, env, ctx) {
    if (req.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }
    const url = new URL(req.url);
    if (req.method === "POST" && url.pathname === "/api/edit_request") {
      try {
        const form = await req.formData();

        const name        = (form.get("name")||"").trim();
        const father      = (form.get("father")||"").trim();
        const grandfather = (form.get("grandfather")||"").trim();
        const email       = (form.get("email")||"").trim();
        const phoneRaw    = (form.get("phone")||"").trim();
        const phoneISO    = (form.get("phone_country_iso")||"").trim();
        const phoneDial   = (form.get("phone_dial_code")||"").trim();
        const message     = (form.get("message")||"").trim();

        const missing = [];
        if (!name)        missing.push("name");
        if (!father)      missing.push("father");
        if (!grandfather) missing.push("grandfather");
        if (!email)       missing.push("email");
        if (!message)     missing.push("message");
        if (missing.length) return json({ ok:false, error:`Missing: ${missing.join(", ")}` }, 400);

        const phoneE164 = (phoneDial && phoneRaw)
          ? `+${phoneDial}${phoneRaw.replace(/[^\d]/g,"")}`
          : "";

        const ua = req.headers.get("user-agent") || "";
        const ip = req.headers.get("cf-connecting-ip") || "";

        await env.DB.prepare(
          `INSERT INTO edit_requests
           (name, father, grandfather, email, phone_e164, phone_iso, phone_dial, message, user_agent, ip)
           VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)`
        ).bind(name, father, grandfather, email, phoneE164, phoneISO, phoneDial, message, ua, ip).run();

        await sendMail(env, {
          to: env.ADMIN_EMAIL,
          subject: `New Edit/Add Request — ${env.SITE_NAME}`,
          html: `
            <h2>New request</h2>
            <p><b>Name:</b> ${escapeHTML(name)}</p>
            <p><b>Father:</b> ${escapeHTML(father)}</p>
            <p><b>Grandfather:</b> ${escapeHTML(grandfather)}</p>
            <p><b>Email:</b> ${escapeHTML(email)}</p>
            <p><b>Phone (E.164):</b> ${escapeHTML(phoneE164)}</p>
            <p><b>Message:</b><br>${nl2br(escapeHTML(message))}</p>
            <hr>
            <p><small>IP: ${escapeHTML(ip)} | UA: ${escapeHTML(ua)}</small></p>
          `
        });

        await sendMail(env, {
          to: email,
          subject: `sisneripoudel.com — ${env.SITE_NAME}`,
          html: `
            <p>Namaste,</p>
            <p>We received your add/edit request. Thank you! We'll review and follow up if we need any clarification.</p>
            <p><b>Summary:</b></p>
            <ul>
              <li>Name: ${escapeHTML(name)}</li>
              <li>Father: ${escapeHTML(father)}</li>
              <li>Grandfather: ${escapeHTML(grandfather)}</li>
              <li>Email: ${escapeHTML(email)}</li>
              <li>Phone: ${escapeHTML(phoneE164)}</li>
              <li>Message: ${escapeHTML(message)}</li>
            </ul>
            <p>— ${env.SITE_NAME}</p>
          `
        });

        return json({ ok:true }, 200);
      } catch (err) {
        return json({ ok:false, error:String(err) }, 500);
      }
    }
    return new Response("Not found", { status: 404 });
  }
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
  };
}

function json(obj, status=200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type":"application/json", ...corsHeaders() }
  });
}

async function sendMail(env, { to, subject, html, replyTo }) {
  const payload = {
    from: `Sisneri Poudel Family Tree <no-reply@sisneripoudel.com>`,
    to,
    subject,
    html,
    reply_to: replyTo || env.ADMIN_EMAIL
  };

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!r.ok) {
    const text = await r.text();
    throw new Error(`Resend mail failed: ${r.status} ${text}`);
  }
}

const escapeHTML = s => s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const nl2br = s => s.replace(/\n/g, "<br>");
