import glob
import javalang
from javalang.parser import JavaSyntaxError


def getMethods(types_list):
    results = []
    
    for t in types_list:
        if type(t) == javalang.tree.MethodDeclaration:
            if type(t.return_type) == type(None):
                results.append(t.name+"; "+str(t.return_type))
            else:
                results.append(t.name+"; "+str(t.return_type.name))
        if type(t) == javalang.tree.ClassDeclaration:
            results += getMethods(t.body)
    
    return results

error_counter = 0

REPOSITORY_NAME = "XYZ"

files_list = glob.glob(f'{REPOSITORY_NAME}/**/*.java', recursive=True)

with open(f'{REPOSITORY_NAME}.txt', 'w') as out_file:
    for file in files_list:
        if "test" in file: # skip dedicated test-files
            continue
        if "module-info.java" in file: # skip module info files
            continue
        with open(file, 'r') as javafile:
            lines = javafile.read()

            # MARK: some newer Java stuff is not parseable and must be removed
            # remove @Nullable annotation
            lines_without_Nullable = lines.replace('@Nullable ', '')

            #remove NonNull annotation
            lines_without_NonNull = lines_without_Nullable.replace('@NonNull ', '')

            # add 'private' for WeakOuter instances
            # TODO: replace this with RegEx or similar
            reduced_lines = lines_without_NonNull \
                    .replace('@WeakOuter\n  class', '@WeakOuter\n  private class') \
                    .replace('@WeakOuter\n   class', '@WeakOuter\n   private class') \
                    .replace('@WeakOuter\n    class', '@WeakOuter\n    private class') \
                    .replace('@WeakOuter\n     class', '@WeakOuter\n     private class') \
                    .replace('@WeakOuter\n      class', '@WeakOuter\n      private class') \
                    .replace('@WeakOuter\n       class', '@WeakOuter\n       private class') \
                    .replace('@WeakOuter\n        class', '@WeakOuter\n        private class') \
                    .replace('@WeakOuter\n         class', '@WeakOuter\n         private class') \
                    .replace('@WeakOuter\n          class', '@WeakOuter\n          private class') \
                    .replace('@WeakOuter\n           class', '@WeakOuter\n           private class') \
                    .replace('@WeakOuter\n            class', '@WeakOuter\n            private class') \
                    .replace('@WeakOuter\n             class', '@WeakOuter\n             private class') \
                    .replace('@WeakOuter\n              class', '@WeakOuter\n              private class') \
                    .replace('@WeakOuter\n               class', '@WeakOuter\n               private class') \

            try:
                tree = javalang.parse.parse(reduced_lines)
                methods_list = getMethods(tree.types)
                out_file.write(file+": " + str(methods_list) + "\n")
            except JavaSyntaxError as pe:
                print(f"ParsingError in: {file} - {pe.description} - {pe.at}")
                error_counter += 1
            except:
                error_counter += 1
                print(f"ParsingError in: {file}")

print(f"number of errors during parsing: {error_counter}")