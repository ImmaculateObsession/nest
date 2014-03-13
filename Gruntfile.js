module.exports = function(grunt) {
    // set up grunt
    grunt.initConfig({
        jshint: {
            src: ['Gruntfile.js', 'static/sass/javascripts/*.js'],
            options: {
                curly: true,
                eqeqeq: false,
                immed: true,
                latedef: true,
                newcap: true,
                noarg: true,
                sub: true,
                undef: true,
                boss: true,
                eqnull: true,
                browser: true,
                trailing: true,
                multistr: true,
                globals: {
                    require: true,
                    define: true,
                    requirejs: true,
                    describe: true,
                    expect: true,
                    it: true,
                    jQuery: true,
                    mixpanel: true,
                    module: true
                }
            }
        },
        watch: {
            files: '<%= jshint.src %>',
            tasks: ['jshint']
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['jshint', 'compliment']);
    grunt.registerTask('compliment', function() {
        grunt.log.writeln('You look nice today!');
    });
};