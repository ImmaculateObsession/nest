module.exports = function(grunt) {
    // set up grunt
    grunt.initConfig({
        jshint: {
            src: ['Gruntfile.js', 'sass/javascripts/*.js'],
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
        },
        cssmin: {
            css: {
                expand: true,
                cwd: 'sass/stylesheets/',
                src: ['*.css'],
                dest: 'compiled/'
            }
        },
        compass: {
            dev: {
                options: {
                    sassDir: 'sass',
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-compass');

    grunt.registerTask('default', ['jshint', 'cssmin:css', 'compliment']);
    grunt.registerTask('compliment', function() {
        grunt.log.writeln('You look nice today!');
    });
};