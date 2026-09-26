"""Set up Casvi with account credentials and selected children."""
import hashlib
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .api import CasviClient, CasviAuthError, CasviError
from .const import DOMAIN, DEFAULT_INTERVAL

SCHEMA = vol.Schema({
    vol.Required("username"): str,
    vol.Required("password"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
})


class CasviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            client = CasviClient(user_input["username"].strip(), user_input["password"])
            try:
                children = await client.authenticate()
                await self.async_set_unique_id(hashlib.sha256(client.username.encode()).hexdigest())
                self._abort_if_unique_id_configured()
                self._credentials = {"username": client.username, "password": user_input["password"]}
                self._children = children
            except CasviAuthError:
                errors["base"] = "invalid_auth"
            except CasviError:
                errors["base"] = "cannot_connect"
            else:
                if not children:
                    return self.async_abort(reason="no_children")
                return await self.async_step_children()
            finally:
                await client.close()
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)

    async def async_step_children(self, user_input=None):
        errors = {}
        if user_input is not None:
            chosen = user_input["children"]
            if chosen and all(key in self._children for key in chosen):
                return self.async_create_entry(title="Casvi", data={
                    **self._credentials, "children": {k: self._children[k] for k in chosen},
                })
            errors["base"] = "select_children"
        return self.async_show_form(step_id="children", errors=errors, data_schema=vol.Schema({
            vol.Required("children", default=list(self._children)): selector.SelectSelector(
                selector.SelectSelectorConfig(multiple=True, options=[
                    {"value": k, "label": v} for k, v in self._children.items()
                ])
            ),
        }))

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors = {}
        if user_input is not None:
            client = CasviClient(entry.data["username"], user_input["password"])
            try:
                await client.authenticate()
            except CasviAuthError:
                errors["base"] = "invalid_auth"
            except CasviError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data_updates={"password": user_input["password"]})
            finally:
                await client.close()
        return self.async_show_form(step_id="reauth_confirm", errors=errors, data_schema=vol.Schema({
            vol.Required("password"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
        }))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CasviOptionsFlow()


class CasviOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        targets = sorted(set(self.config_entry.options.get("notify_targets", [])) | {
            name for name in self.hass.services.async_services().get("notify", {})
            if name.startswith("mobile_app_")
        })
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required("notify_targets", default=self.config_entry.options.get("notify_targets", [])): selector.SelectSelector(
                selector.SelectSelectorConfig(multiple=True, options=targets)
            ),
            vol.Required("interval", default=self.config_entry.options.get("interval", DEFAULT_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=120)),
            vol.Required("message_limit", default=self.config_entry.options.get("message_limit", 50)): vol.All(vol.Coerce(int), vol.Range(min=10, max=100)),
        }))
