#!/usr/bin/python3

"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review

def parse(arg):
    curly_braces_pattern = r"\{(.*?)\}"
    brackets_pattern = r"\[(.*?)\]"

    curly_braces_match = re.search(curly_braces_pattern, arg)
    brackets_match = re.search(brackets_pattern, arg)

    if not curly_braces_match:
        if not brackets_match:
            return [i.strip(",") for i in split(arg)]
        else:
            before_brackets = arg[:brackets_match.span()[0]]
            lexer = split(before_brackets)
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets_match.group())
            return retl
    else:
        before_curly_braces = arg[:curly_braces_match.span()[0]]
        lexer = split(before_curly_braces)
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces_match.group())
        return retl



class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB command interpreter.

    Attributes:
        prompt (str): The command prompt.
    """
    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True


    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Create a new class instance and print its id.
        """
        argls = parse(arg)
        if len(argls) == 0:
            print("** class name missing **")
        elif argls[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(argls[0])().id)
            storage.save()


    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl = parse(arg)
        count = sum(1 for obj in storage.all().values() if argl[0] == obj.__class__.__name__)
        print(count)

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }

        # Regular expression to match the command format
        pattern = r"^(\w+)\.(\w+)\((.*?)\)$"
        match = re.match(pattern, arg)

        if match:
            obj_name, method_name, params = match.groups()
            if method_name in argdict:
                call = f"{obj_name} {params}"
                return argdict[method_name](call)

        print(f"*** Unknown syntax: {arg}")
        return False


    def do_show(self, arg):
        """
        Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        args = parse(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        instance_id = args[1].strip('"\'')  # Remove quotes if present

        objdict = storage.all()
        key = f"{class_name}.{instance_id}"

        if key not in objdict:
            print("** no instance found **")
        else:
            instance = objdict[key]
            print(str(instance))


    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        argls = parse(arg)
        objdict = storage.all()
        if len(argls) == 0:
            print("** class name missing **")
        elif argls[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argls) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argls[0], argls[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(argls[0], argls[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argl = parse(arg)
        if argl and argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            if argl:
                class_name = argl[0]
                for obj in storage.all().values():
                    if obj.__class__.__name__ == class_name:
                        objl.append(obj.__str__())
            else:
                for obj in storage.all().values():
                    objl.append(obj.__str__())
            print(objl)


    def do_update(self, arg):
        """
        Usage: update <class> <id> <attribute_name> <attribute_value> or
            <class>.update(<id>, <attribute_name>, <attribute_value>) or
            <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary.
        """
        args = parse(arg)
        objdict = storage.all()

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        instance_id = args[1]
        key = f"{class_name}.{instance_id}"

        if key not in objdict:
            print("** no instance found **")
            return

        obj = objdict[key]

        if len(args) < 3:
            print("** attribute name missing **")
            return

        attribute_name = args[2]

        if len(args) < 4:
            obj.__dict__[attribute_name] = ""
            storage.save()
            return

        attribute_value = args[3]

        try:
            value = eval(attribute_value)
        except (NameError, SyntaxError):
            value = attribute_value

        if isinstance(value, dict):
            for key, val in value.items():
                setattr(obj, key, val)
        else:
            setattr(obj, attribute_name, value)

        storage.save()

if __name__ == '__main__':
    HBNBCommand().cmdloop()