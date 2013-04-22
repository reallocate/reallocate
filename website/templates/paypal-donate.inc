{# Donation purpose and donation_purpose_token must be set if not for reallocate slushfund #}
<div class='paypal-done' style='margin:15px;text-align:center;{% if donation_purpose %}width:200px;{% endif %}'{% if donation_purpose %}title="This donation will be routed through reallocate."{% endif %}>
    {% if donation_purpose %}<strong> Donate to <br/>{{ donation_purpose }}</strong>{% endif %}
    <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top" alt="heeey">
    <input type="hidden" name="cmd" value="_donations">
    <input type="hidden" name="business" value="tim@reallocate.org">
    <input type="hidden" name="notify_url" value="/paypal?email={{ user_email }}{% if donation_purpose %}&purpose={{ donation_purpose_token }}{% endif %}"/>
    <input type="hidden" name="lc" value="US">
    <input type="hidden" name="item_name" value="Reallocate{% if donation_purpose %} - {{ donation_purpose }} {% endif %}">
    <input type="hidden" name="no_note" value="0">
    <input type="hidden" name="currency_code" value="USD">
    <input type="hidden" name="bn" value="PP-DonationsBF:btn_donate_LG.gif:NonHostedGuest">
    <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
    <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
    </form>
</div>