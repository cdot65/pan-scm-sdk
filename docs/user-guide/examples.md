# Examples

This section provides practical examples of how to use `pan-scm-sdk` commands.

## Example 1: Creating the Secrets File

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone create-secrets-file
```

</div>

Follow the prompts to input your SCM credentials.

## Example 2: Cloning Address Objects

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone clone-address-objects
```

</div>

**Sample Output:**

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone clone-address-groupsStarting address objects migration...
Retrieved 15 address objects from source.
Successfully created 15 address objects in destination.
AddressModel objects migration completed successfully.
```

</div>

## Example 3: Cloning Address Groups

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone clone-address-groups
```

</div>

**Sample Output:**

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone clone-address-groups
Starting address groups migration...
Retrieved 8 address groups from source.
Successfully created 8 address groups in destination.
AddressModel groups migration completed successfully.
```

</div>

## Example 4: Specifying a Custom Settings File

If you have a custom settings file, you can specify it using the `--settings-file` option:

<div class="termy">

<!-- termynal -->

```bash
$ scm-clone clone-address-objects --settings-file custom_secrets.yaml
```

</div>

---

Feel free to combine options as needed to suit your workflow.

If you run into any issues, consider visiting the [Troubleshooting](troubleshooting.md) guide.