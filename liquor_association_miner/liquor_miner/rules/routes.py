from flask import render_template, request, redirect, url_for, session
from . import rules_bp
from ..analysis import get_association_rules, get_unique_items, get_recommendations


@rules_bp.route('/')
def home():
    """Home Page"""
    return render_template('home.html')


@rules_bp.route('/rules')
def rules():
    """Rules Page: Fetches and displays all association rules."""
    rules_list = get_association_rules()

    if rules_list and isinstance(rules_list, list) and "error" in rules_list[0]:
        return render_template('rules.html', rules=[], error=rules_list[0]["error"])

    return render_template('rules.html', rules=rules_list)


# liquor_miner/rules/routes.py (Ensure your function looks like this)

@rules_bp.route('/combo-offers', methods=['GET', 'POST'])
def combo_offers():
    all_rules = get_association_rules()
    unique_items = get_unique_items()
    error = None

    # CRITICAL: is_filtered is True if the form was submitted (POST)
    is_filtered = (request.method == 'POST')

    if all_rules and isinstance(all_rules, list) and "error" in all_rules[0]:
        error = all_rules[0]["error"]
        all_rules = []

    # --- Conditional Logic to Hide Results on Initial Load (GET) ---
    if request.method == 'GET':
        combo_list = []
        selected_item = None
    else:
        # If POST (filtered), proceed with fetching and filtering rules

        # 1. Start with all multi-item antecedents (global combo rules)
        combo_list = [
            rule for rule in all_rules
            if len(rule['antecedent']) > 1
        ]

        # Get the selected item from the form
        selected_item = request.form.get('item_select')

        # 2. Filter further if a specific item was selected
        if selected_item and selected_item != "All Combos":
            combo_list = [
                rule for rule in combo_list
                if rule['consequent'] == selected_item
            ]

        # Final cleanup for the template display
        combo_list.sort(key=lambda x: x['lift'], reverse=True)
        selected_item = selected_item if selected_item != "All Combos" else None

    return render_template(
        'combo_offers.html',
        all_combos=combo_list,
        unique_items=unique_items,
        selected_item=selected_item,
        error=error,
        is_filtered=is_filtered  # Pass the new tracking variable to the template
    )

@rules_bp.route('/recommend', methods=['GET', 'POST'])
def recommend():
    """Recommendation Selection Page: Single-item selection."""

    unique_items = get_unique_items()
    error = None

    if unique_items and isinstance(unique_items, list) and "error" in unique_items[0]:
        error = unique_items[0]["error"]
        unique_items = []

    if request.method == 'POST' and not error:
        selected_item = request.form.get('item_select')

        if selected_item:
            recommendations = get_recommendations(selected_item)

            # Store results and selected item in session for the results page
            session['recommendations'] = recommendations
            session['selected_item'] = selected_item

            # Redirect to the dedicated result page
            return redirect(url_for('rules.result'))

    # Render the selection form
    return render_template(
        'recommend.html',
        items=unique_items,
        error=error
    )


@rules_bp.route('/result')
def result():
    """Result Page: Displays recommendations from session data."""
    # Retrieve and pop data from session (pop removes it after reading)
    recommendations = session.pop('recommendations', [])
    selected_item = session.pop('selected_item', None)

    error = None
    if recommendations and isinstance(recommendations, list) and "error" in recommendations[0]:
        error = recommendations[0]["error"]
        recommendations = []

    if not selected_item:
        # If no item was found in the session, redirect back to the selection page
        return redirect(url_for('rules.recommend'))

    return render_template(
        'result.html',
        selected_item=selected_item,
        recommendations=recommendations,
        error=error
    )


@rules_bp.route('/about')
def about():
    """About Page"""
    return render_template('about.html')