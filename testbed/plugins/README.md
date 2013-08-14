#Plugins

Plugins are WIP hence the code plugin code lives in testbed.
modules in /testbed/plugins are available to the plugin manager due to the path being set in /proto/arcyd and /runtime_tests.sh manually.

##Use
Plugins must register which functions they want called at certain hooks.
They must define `getHooks()` which returns a list of tuples such as `[("hookName", onHookName)]` where `onHookName` is the function to be called when the hook is executed.

The function must accept 1 argument which will be a dict of all the parameters sent by the hook. To see what is in the dict look at the source where the hook is fired.

The plugin must then be added to the repo configuration file as `--plugins PLUGIN`
##Example
    def printSomeStuffBeforeReviewCreation(params):
        print "A review is about to be created"

    def getHooks():
        return [("beforeCreateReview", printSomeStuffBeforeReviewCreation)]
##Testing
The regular tests do not load plugins but can be made to by passing a PluginManager with the required plugins loaded
