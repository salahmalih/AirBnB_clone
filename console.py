#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from models import storage
from shlex import split
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review

def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)

    def split_arg(arg):
        return arg.split(',')

    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split_arg(arg)]
        else:
            lexer = split_arg(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split_arg(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
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

    
    def do_show(self, arg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        argls = parse(arg)
        objdict = storage.all()
        if len(argls) == 0:
            print("** class name missing **")
        elif argls[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argls) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argls[0], argls[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(argls[0], argls[1])])

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
        if len(argl) > 0 and argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            for obj in storage.all().values():
                if len(argl) > 0 and argl[0] == obj.__class__.__name__:
                    objl.append(obj.__str__())
                elif len(argl) == 0:
                    objl.append(obj.__str__())
            print(objl)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
        <class>.update(<id>, <attribute_name>, <attribute_value>) or
        <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""

        argls = parse(arg)
        objdict = storage.all()

        if not argls:
            print("** class name missing **")
            return False

        class_name = argls[0]

        if class_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False

        if len(argls) < 2:
            print("** instance id missing **")
            return False

        instance_id = argls[1]

        if f"{class_name}.{instance_id}" not in objdict.keys():
            print("** no instance found **")
            return False

        if len(argls) < 3:
            print("** attribute name missing **")
            return False

        attribute_name = argls[2]

        if len(argls) < 4:
            print("** value missing **")
            return False

        attribute_value = argls[3]

        obj = objdict[f"{class_name}.{instance_id}"]
        class_dict = obj.__class__.__dict__

        if attribute_name in class_dict:
            val_type = type(class_dict[attribute_name])
            obj.__dict__[attribute_name] = val_type(attribute_value)
        elif isinstance(eval(attribute_value), dict):
            for key, value in eval(attribute_value).items():
                if key in class_dict and type(class_dict[key]) in {str, int, float}:
                    val_type = type(class_dict[key])
                    obj.__dict__[key] = val_type(value)
                else:
                    obj.__dict__[key] = value
        else:
            obj.__dict__[attribute_name] = attribute_value

        storage.save()

if __name__ == '__main__':
    HBNBCommand().cmdloop()