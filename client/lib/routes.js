class Route {

    name;
    path;
    view;

    /**
     * Data struct for routing
     * @param {string} name Hyperlink text
     * @param {string} path The route
     * @param {string} view Which component to display on this route
     */
    constructor(name, path, view) {
        this.name = name;
        this.path = path;
        this.view = view;
    }

    isDevTool() {
        return this.path.startsWith('/devtools');
    }

    isMenu() {
        return this.path === '/menu';
    }

    isRoot() {
        return this.path === '/';
    }

    isLoad() {
        return this.path === '/';
    }

}


class RouteManager {

    static ROUTES = [
        new Route(
            'Loading',
            '/',
            '<loading-view></loading-view>',
        ),
        new Route(
            'Organizer',
            '/organizer',
            '<organizer-view></organizer-view>',
        ),
        new Route(
            'Menu',
            '/menu',
            '<menu-view></menu-view>',
        ),
        new Route(
            'Settings',
            '/settings',
            '<settings-view></settings-view>',
        ),
        new Route(
            'Deep Learning',
            '/devtools/check-rate',
            '<check-rate-view></check-rate-view>',
        ),
        new Route(
            'Clustering Algorithms',
            '/devtools/histogram',
            '<histogram-view></histogram-view>',
        ),
        new Route(
            'Data Labeling',
            '/devtools/label-data',
            '<label-data-view></label-data-view>',
        ),
        new Route(
            'Data Management',
            '/devtools/data-transfer',
            '<transfer-data-view></transfer-data-view>',
        ),
        new Route(
            'Check Status',
            '/devtools/check-status',
            '<status-view></status-view>',
        ),
        new Route(
            'Model Summary',
            '/devtools/model-summary',
            '<model-summary-view></model-summary-view>',
        ),
    ];

    static menu1() {
        return RouteManager.ROUTES.filter(e => !(e.isDevTool() || e.isMenu() || e.isRoot()));
    }

    static menu2() {
        return RouteManager.ROUTES.filter(e => e.isDevTool());
    }

    static checkRate() {
        return RouteManager.ROUTES.find(element => element.view === '<check-rate-view></check-rate-view>');
    }

    static modelSummary() {
        return RouteManager.ROUTES.find(element => element.view === '<model-summary-view></model-summary-view>');
    }

}


export default RouteManager;
