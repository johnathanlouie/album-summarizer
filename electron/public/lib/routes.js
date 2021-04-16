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
        return this.path.startsWith('/menu');
    }

    isRoot() {
        return this.path.startsWith('/');
    }

}


class RouteManager {

    static ROUTES = [
        new Route(
            'Organizer',
            '/',
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
            'Data Preparation',
            '/devtools/label-data',
            '<label-data-view></label-data-view>',
        ),
        new Route(
            'Data Transfer',
            '/devtools/data-transfer',
            '<transfer-data-view></transfer-data-view>',
        ),
        new Route(
            'Check Status',
            '/devtools/check-status',
            '<status-view></status-view>',
        ),
    ];

    static menu1() {
        return RouteManager.ROUTES.filter(e => !(e.isDevTool() || e.isMenu()));
    }

    static menu2() {
        return RouteManager.ROUTES.filter(e => e.isDevTool());
    }

}


export default RouteManager;
