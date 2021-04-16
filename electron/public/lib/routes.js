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
            'Organizer',
            '/organizer',
            '<organizer-view></organizer-view>',
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
    ];

}


export default RouteManager;
