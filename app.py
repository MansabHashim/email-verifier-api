from flask import Flask, request, jsonify
import dns.resolver
import smtplib
import socket

app = Flask(__name__)

def verify_email(email):
    try:
        user, domain = email.split('@')
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo("example.com")
        server.mail("test@example.com")
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return "valid"
        elif code == 550:
            return "invalid"
        else:
            return "catch-all or unknown"
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return "invalid domain"
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout):
        return "smtp error"
    except Exception as e:
        return f"error: {str(e)}"

@app.route("/verify", methods=["GET"])
def verify():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400
    status = verify_email(email)
    return jsonify({"email": email, "status": status})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
