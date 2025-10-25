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

        // Insert the new request
        await env.DB.prepare(
          `INSERT INTO edit_requests
           (name, father, grandfather, email, phone_e164, phone_iso, phone_dial, message, user_agent, ip)
           VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)`
        ).bind(name, father, grandfather, email, phoneE164, phoneISO, phoneDial, message, ua, ip).run();

        // ===== NEW: build the admin table (most recent first) =====
        // Use rowid for recency ordering (works even if there's no created_at column)
        // Query all rows, newest first, using created_at then id
        const rs = await env.DB.prepare(
          `SELECT id, name, father, grandfather, email, phone_e164, phone_iso, phone_dial,
                  message, user_agent, ip, created_at
          FROM edit_requests
          ORDER BY datetime(created_at) DESC, id DESC`
        ).all();

        const rows = rs.results || [];
        const adminTable = renderAdminHTMLTable(rows);
        const adminEmails = (env.ADMIN_EMAILS || "")
          .split(",")
          .map(s => s.trim())
          .filter(Boolean);

        // ===== CHANGED: admin email now goes to both addresses =====
        await sendMail(env, {
          to: ["aashish.pd@gmail.com", "sisneripoudel@gmail.com"],
          subject: `New Edit/Add Request — ${env.SITE_NAME}`,
          html: `
            <h2>New request (latest submission at top of table below)</h2>
            ${renderKeyValues({
              Name: name, Father: father, Grandfather: grandfather, Email: email,
              "Phone (E.164)": phoneE164, Message: message, IP: ip, "User-Agent": ua
            })}
            <hr>
            <h3>All edit_requests (most recent first)</h3>
            <p style="font:14px system-ui;margin:6px 0;">Row count: ${rows.length}</p>
            ${rows.length ? adminTable : '<p style="font:14px system-ui;color:#666;">(No rows found in edit_requests)</p>'}
          `
        });

        // ===== CONFIRMATION to the submitter (kept, slightly tidied) =====
        await sendMail(env, {
          to: email,
          subject: `sisneripoudel.com — ${env.SITE_NAME}`,
          html: `
            <p>Namaste,</p>
            <p>We received your add/edit request. Thank you! We'll review and follow up if we need any clarification.</p>
            <p><b>Summary:</b></p>
            ${renderKeyValues({
              Name: name,
              Father: father,
              Grandfather: grandfather,
              Email: email,
              Phone: phoneE164,
              Message: message
            })}
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

// === helper to render key/value block nicely in HTML
function renderKeyValues(obj){
  const rows = Object.entries(obj).map(([k,v]) => `
    <tr>
      <th align="left" style="padding:6px 10px;border-bottom:1px solid #eee;white-space:nowrap;">${escapeHTML(k)}</th>
      <td style="padding:6px 10px;border-bottom:1px solid #eee;">${nl2br(escapeHTML(String(v ?? "")))}</td>
    </tr>`).join("");
  return `<table style="border-collapse:collapse;border:1px solid #eee;border-radius:8px;overflow:hidden;font:14px system-ui, -apple-system, Segoe UI, Roboto, Arial;">
    <tbody>${rows}</tbody>
  </table>`;
}

// === NEW: admin table renderer
function renderAdminHTMLTable(rows){
  const header = `
    <thead>
      <tr style="background:#f7f9fb;">
        <th align="left">#</th>
        <th align="left">Name</th>
        <th align="left">Father</th>
        <th align="left">Grandfather</th>
        <th align="left">Email</th>
        <th align="left">Phone</th>
        <th align="left">ISO</th>
        <th align="left">Dial</th>
        <th align="left">Message</th>
        <th align="left">IP</th>
        <th align="left">User-Agent</th>
        <th align="left">Created</th>
      </tr>
    </thead>`;

  const body = rows.map(r => `
    <tr>
      <td style="vertical-align:top;">${escapeHTML(String(r.id ?? ""))}</td>
      <td style="vertical-align:top;">${escapeHTML(r.name ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.father ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.grandfather ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.email ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.phone_e164 ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.phone_iso ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.phone_dial ?? "")}</td>
      <td style="vertical-align:top; max-width:420px;">${nl2br(escapeHTML(r.message ?? ""))}</td>
      <td style="vertical-align:top;">${escapeHTML(r.ip ?? "")}</td>
      <td style="vertical-align:top; max-width:420px;">${escapeHTML(r.user_agent ?? "")}</td>
      <td style="vertical-align:top;">${escapeHTML(r.created_at ?? "—")}</td>
    </tr>
  `).join("");

  return `<div style="overflow:auto;">
    <table style="border-collapse:collapse;border:1px solid #e5eef4;border-radius:10px;overflow:hidden;font:13px system-ui, -apple-system, Segoe UI, Roboto, Arial; min-width:900px;">
      ${header}
      <tbody>${body}</tbody>
    </table>
  </div>`;
}


async function sendMail(env, { to, subject, html, replyTo }) {
  const payload = {
    from: `Sisneri Poudel Family Tree <no-reply@sisneripoudel.com>`,
    // Resend accepts string or string[]
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
