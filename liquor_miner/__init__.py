from flask import Flask


def create_app(test_config=None):
    app = Flask('liquor_miner', instance_relative_config=True)

    # CRITICAL FIX: Secret key required for Flask sessions (used by the /recommend and /result routes)
    app.config['SECRET_KEY'] = 'a_strong_and_secret_key_for_sessions_123'

    with app.app_context():
        from .rules import rules_bp
        app.register_blueprint(rules_bp)

    return app